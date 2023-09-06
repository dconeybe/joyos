from __future__ import annotations

from collections.abc import Sequence
import dataclasses
import hashlib
import pathlib
import tarfile
from typing import Optional, TypedDict
import urllib.parse

from absl import app
from absl import logging
from absl import flags
import requests


FLAG_BUILD_DIR = flags.DEFINE_string(
    "build_dir",
    None,
    "The directory into which downloaded files will be saved and extracted and in which the build "
    "of the cross compiler will actually occur. This directory may be safely deleted after a "
    "successful execution of this application. If not specified then the current directoryw will "
    "be used. This directory will be created if it does not exist.",
)

FLAG_DEST_DIR = flags.DEFINE_string(
    "dest_dir",
    None,
    "The directory into which the cross compiler will ultimately be installed. "
    "If this directory does not exist then it will be created.",
    required=True,
)

FLAG_DOWNLOAD_DIR = flags.DEFINE_string(
    "download_dir",
    None,
    "The directory into which downloaded files will be saved. If specified, when a file would "
    "otherwise be downloaded, this directory will first be checked for a previous successful "
    "download of the file and, if found, it will be used instead of re-downloading the file. "
    "If not specified, then the build directory will be used.",
)


class CrossCompilerBuilder:

  def __init__(
      self,
      dest_dir: pathlib.Path,
      build_dir: Optional[pathlib.Path],
      download_dir: Optional[pathlib.Path],
  ) -> None:
    self.dest_dir = dest_dir
    self.build_dir = build_dir
    self.download_dir = download_dir

    self._downloaded_file_by_id: dict[str, pathlib.Path] = {}

  def effective_build_dir(self) -> pathlib.Path:
    return self.build_dir if self.build_dir is not None else pathlib.Path.cwd()

  def effective_download_dir(self) -> pathlib.Path:
    return self.download_dir if self.download_dir is not None else self.effective_build_dir()

  def run(self) -> None:
    logging.info(
        "Building a cross compiler in %s to install in %s",
        self.dest_dir,
        self.effective_build_dir(),
    )
    self._create_directory_if_not_exists(self.build_dir)
    self._create_directory_if_not_exists(self.download_dir)
    self._download_files()
    self._build_binutils()

  def _create_directory_if_not_exists(self, dir_path: Optional[pathlib.Path]) -> None:
    if dir_path is None or dir_path.is_dir():
      return
    logging.info("Creating directory: %s", dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)

  def _download_files(self) -> None:
    file_download_count = 0
    file_download_total_bytes = 0
    file_download_cache_used_count = 0
    file_download_cache_total_bytes = 0

    for download_id, download_info in self._file_download_infos().items():
      parsed_url = urllib.parse.urlparse(download_info.url)
      url_path = pathlib.PurePosixPath(parsed_url.path)
      dest_file = self.effective_download_dir() / url_path.name
      self._downloaded_file_by_id[download_id] = dest_file

      if dest_file.is_file():
        logging.info("Verifying SHA512 hash of previously-downloaded file: %s", dest_file)
        sha512_hash_calculator = hashlib.new("sha512")
        download_cache_bytes = 0
        with dest_file.open("rb") as f:
          while True:
            chunk = f.read1()
            if not chunk:
              break
            sha512_hash_calculator.update(chunk)
            download_cache_bytes += len(chunk)
        sha512_hexdigest = sha512_hash_calculator.hexdigest()
        if sha512_hexdigest == download_info.sha512_hexdigest:
          file_download_cache_used_count += 1
          file_download_cache_total_bytes += download_cache_bytes
          logging.info(
              "Verifying SHA512 hash of previously-downloaded file %s completed successfully "
              "(%s bytes); skipping download of %s",
              dest_file,
              f"{download_cache_bytes:,}",
              download_info.url,
          )
          continue
        logging.info(
            "Verification of SHA512 hash of previously-downloaded file %s failed: "
            "got %s but expected %s; file will be re-downloaded",
            dest_file,
            sha512_hexdigest,
            download_info.sha512_hexdigest,
        )

      logging.info("Downloading %s to %s", download_info.url, dest_file)
      file_download_count += 1
      response = requests.get(download_info.url, stream=True)
      sha512_hash_calculator = hashlib.new("sha512")
      downloaded_bytes_count = 0
      with dest_file.open("wb") as f:
        for chunk in response.iter_content(chunk_size=None):
          f.write(chunk)
          file_download_total_bytes += len(chunk)
          downloaded_bytes_count += len(chunk)
          sha512_hash_calculator.update(chunk)
      logging.info(
          "Downloading %s to %s complete (%s bytes)",
          download_info.url,
          dest_file,
          f"{downloaded_bytes_count:,}",
      )

      sha512_hexdigest = sha512_hash_calculator.hexdigest()
      if sha512_hexdigest != download_info.sha512_hexdigest:
        raise Sha512MismatchError(
            f"SHA512 hash of downloaded file {download_info.url} differs from the expected value: "
            f"got {sha512_hexdigest} but expected {download_info.sha512_hexdigest}"
        )

    logging.info(
        "Downloaded %s files (%s bytes)", file_download_count, f"{file_download_total_bytes:,}"
    )
    logging.info(
        "Used %s previously-downloaded files (%s bytes)",
        file_download_cache_used_count,
        f"{file_download_cache_total_bytes:,}",
    )

  def _build_binutils(self) -> None:
    file_download_info = self._file_download_infos()["binutils"]
    binutils_archive_file = self._downloaded_file_by_id["binutils"]
    self._extract_archive(
        archive_file=binutils_archive_file,
        dest_dir=self.effective_build_dir(),
        file_download_info=file_download_info,
    )

  def _extract_archive(
      self, archive_file: pathlib.Path, dest_dir: pathlib.Path, file_download_info: FileDownloadInfo
  ) -> None:
    extracted_subdir = dest_dir / file_download_info.extracted_subdir_name
    stamp_file = dest_dir / f"{file_download_info.extracted_subdir_name}.extract.stamp.txt"

    try:
      with stamp_file.open("rb") as f:
        stamp_file_bytes = f.read(4 * len(file_download_info.sha512_hexdigest))
    except IOError as e:
      logging.debug(
          "Error reading stamp file %s; deleting the directory and re-extracting %s",
          stamp_file,
          archive_file,
      )
    else:
      if stamp_file_bytes.decode("utf8", errors="replace") == file_download_info.sha512_hexdigest:
        logging.info(
            "Skipping extracting %s to %s since it appears to have been already extracted",
            archive_file,
            dest_dir,
        )
        return

    logging.info("Extracting %s to %s", archive_file, dest_dir)
    with tarfile.open(archive_file, "r") as f:
      # TODO(py311) Add filter=data to the extractall() call once the minimum-supported Python
      # version is upgraded to at least 3.11.4 (at the time of writing the minimum-supported Python
      # version is 3.10).
      f.extractall(dest_dir)

    if not extracted_subdir.is_dir():
      raise ArchiveExtractError(
          f"Extracting {archive_file} to {dest_dir} should have created "
          f"{extracted_subdir.relative_to(dest_dir)}, but it was not created"
      )

    stamp_file.write_bytes(file_download_info.sha512_hexdigest.encode("utf8"))

  def _file_download_infos(self) -> FileDownloadInfos:
    return {
        "binutils": FileDownloadInfo(
            extracted_subdir_name="binutils-2.41",
            url="https://ftp.gnu.org/gnu/binutils/binutils-2.41.tar.bz2",
            sha512_hexdigest="8c4303145262e84598d828e1a6465ddbf5a8ff757efe3fd981948854f32b311a"
            "fe5b154be3966e50d85cf5d25217564c1f519d197165aac8e82efcadc9e1e47c",
        ),
        "gcc": FileDownloadInfo(
            extracted_subdir_name="gcc-13.2.0",
            url="https://ftp.gnu.org/gnu/gcc/gcc-13.2.0/gcc-13.2.0.tar.gz",
            sha512_hexdigest="41c8c77ac5c3f77de639c2913a8e4ff424d48858c9575fc318861209467828cc"
            "b7e6e5fe3618b42bf3d745be8c7ab4b4e50e424155e691816fa99951a2b870b9",
        ),
        "mpfr": FileDownloadInfo(
            url="https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.1.tar.gz",
            extracted_subdir_name="mpfr-4.2.1",
            sha512_hexdigest="858b7c2c3018e4099a7cd6d9d38eca7c46af90fa2c307d9417518027f07b6c43"
            "c51152c60b56359a53e7101a5d0629753f3eb5c54e17574742c374830832fcfe",
        ),
        "gmp": FileDownloadInfo(
            extracted_subdir_name="gmp-6.3.0",
            url="https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.gz",
            sha512_hexdigest="44672c7568b007b4dffc5544374b9169004dfbe7ff79712302f15aa95d46229e"
            "3a057266a0421aadf95ab8a4af13ce4090d8ea39615d50c5064b4703a53fe3b0",
        ),
        "mpc": FileDownloadInfo(
            extracted_subdir_name="mpc-1.3.1",
            url="https://ftp.gnu.org/gnu/mpc/mpc-1.3.1.tar.gz",
            sha512_hexdigest="4bab4ef6076f8c5dfdc99d810b51108ced61ea2942ba0c1c932d624360a5473d"
            "f20d32b300fc76f2ba4aa2a97e1f275c9fd494a1ba9f07c4cb2ad7ceaeb1ae97",
        ),
    }


class Sha512MismatchError(Exception):
  pass


class ArchiveExtractError(Exception):
  pass


@dataclasses.dataclass(frozen=True)
class FileDownloadInfo:
  url: str
  sha512_hexdigest: str
  extracted_subdir_name: str


class FileDownloadInfos(TypedDict):
  binutils: FileDownloadInfo
  gcc: FileDownloadInfo
  mpfr: FileDownloadInfo
  gmp: FileDownloadInfo
  mpc: FileDownloadInfo


def main(argv: Sequence[str]) -> None:
  if len(argv) > 1:
    raise app.UsageError(f"Unexpected argument: {argv[1]}")

  dest_dir = pathlib.Path(FLAG_DEST_DIR.value)
  build_dir = pathlib.Path(FLAG_BUILD_DIR.value) if FLAG_BUILD_DIR.value is not None else None
  download_dir = (
      pathlib.Path(FLAG_DOWNLOAD_DIR.value) if FLAG_DOWNLOAD_DIR.value is not None else None
  )

  builder = CrossCompilerBuilder(
      dest_dir=dest_dir,
      build_dir=build_dir,
      download_dir=download_dir,
  )

  builder.run()


if __name__ == "__main__":
  app.run(main)
