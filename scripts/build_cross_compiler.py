from __future__ import annotations

from collections.abc import Sequence
import dataclasses
import hashlib
import pathlib
from typing import Optional
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
    "successful execution of this application. If not specified then the current directoryw will be "
    "used. This directory will be created if it does not exist.",
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

  def _create_directory_if_not_exists(self, dir_path: Optional[pathlib.Path]) -> None:
    if dir_path is None or dir_path.is_dir():
      return
    logging.info("Creating directory: %s", dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)

  def _download_files(self) -> None:
    for download_info in self._file_download_infos():
      parsed_url = urllib.parse.urlparse(download_info.url)
      url_path = pathlib.PurePosixPath(parsed_url.path)
      dest_file = self.effective_download_dir() / url_path.name

      if dest_file.is_file():
        logging.info("Verifying SHA512 hash of previously-downloaded file: %s", dest_file)
        sha512_hash_calculator = hashlib.new("sha512")
        with dest_file.open("rb") as f:
          while True:
            chunk = f.read1()
            if not chunk:
              break
            sha512_hash_calculator.update(chunk)
        sha512_hexdigest = sha512_hash_calculator.hexdigest()
        if sha512_hexdigest == download_info.sha512_hexdigest:
          continue
        logging.info(
            "Verification of SHA512 hash of previously-downloaded file %s failed: "
            "got %s but expected %s; file will be re-downloaded",
            dest_file,
            sha512_hexdigest,
            download_info.sha512_hexdigest,
        )

      logging.info("Downloading %s to %s", download_info.url, dest_file)
      response = requests.get(download_info.url, stream=True)
      sha512_hash_calculator = hashlib.new("sha512")
      downloaded_bytes_count = 0
      with dest_file.open("wb") as f:
        for chunk in response.iter_content(chunk_size=None):
          f.write(chunk)
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

  def _file_download_infos(self) -> list[FileDownloadInfo]:
    return [
        FileDownloadInfo(
            url="https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.1.tar.gz",
            sha512_hexdigest="858b7c2c3018e4099a7cd6d9d38eca7c46af90fa2c307d9417518027f07b6c43"
            "c51152c60b56359a53e7101a5d0629753f3eb5c54e17574742c374830832fcfe",
        ),
        FileDownloadInfo(
            url="https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.gz",
            sha512_hexdigest="44672c7568b007b4dffc5544374b9169004dfbe7ff79712302f15aa95d46229e"
            "3a057266a0421aadf95ab8a4af13ce4090d8ea39615d50c5064b4703a53fe3b0",
        ),
        FileDownloadInfo(
            url="https://ftp.gnu.org/gnu/mpc/mpc-1.3.1.tar.gz",
            sha512_hexdigest="4bab4ef6076f8c5dfdc99d810b51108ced61ea2942ba0c1c932d624360a5473d"
            "f20d32b300fc76f2ba4aa2a97e1f275c9fd494a1ba9f07c4cb2ad7ceaeb1ae97",
        ),
        FileDownloadInfo(
            url="https://ftp.gnu.org/gnu/binutils/binutils-2.41.tar.bz2",
            sha512_hexdigest="8c4303145262e84598d828e1a6465ddbf5a8ff757efe3fd981948854f32b311a"
            "fe5b154be3966e50d85cf5d25217564c1f519d197165aac8e82efcadc9e1e47c",
        ),
        FileDownloadInfo(
            url="https://ftp.gnu.org/gnu/gcc/gcc-13.2.0/gcc-13.2.0.tar.gz",
            sha512_hexdigest="41c8c77ac5c3f77de639c2913a8e4ff424d48858c9575fc318861209467828cc"
            "b7e6e5fe3618b42bf3d745be8c7ab4b4e50e424155e691816fa99951a2b870b9",
        ),
    ]


class Sha512MismatchError(Exception):
  pass


@dataclasses.dataclass(frozen=True)
class FileDownloadInfo:
  url: str
  sha512_hexdigest: str


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
