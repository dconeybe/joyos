set(SRC_FILE "" CACHE STRING "")
if(NOT SRC_FILE)
  message(FATAL_ERROR "-DSRC_FILE:FILEPATH=<file path> must be specified")
endif()

set(DEST_FILE "" CACHE STRING "")
if(NOT DEST_FILE)
  message(FATAL_ERROR "-DDEST_FILE:FILEPATH=<file path> must be specified")
endif()

set(MAIN_O_PATH "" CACHE STRING "")
if(NOT MAIN_O_PATH)
  message(FATAL_ERROR "-DMAIN_O_PATH:STRING=<path to main.o> must be specified")
endif()

configure_file("${SRC_FILE}" "${DEST_FILE}")
