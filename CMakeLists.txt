cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

project(joyos LANGUAGES C CXX ASM)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# Remove -g from the compiler flags so that useless debug information isn't generated.
set(CMAKE_ASM_FLAGS_DEBUG "" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS_DEBUG "" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS_DEBUG "" CACHE STRING "" FORCE)

include(JoyOsSetupCompilerWarnings)

set(
  JOYOS_COMPILE_AND_LINK_OPTIONS
  -fno-exceptions
  -fno-rtti
  -nostartfiles
  -nostdlib
  -ffreestanding
  -m16
  -march=i386
  -fno-pie
  -fno-asynchronous-unwind-tables
)

add_compile_options(
  "${JOYOS_COMPILE_AND_LINK_OPTIONS}"
)

add_link_options(
  "${JOYOS_COMPILE_AND_LINK_OPTIONS}"
  LINKER:--oformat=binary
  "LINKER:SHELL:-T ${CMAKE_CURRENT_LIST_DIR}/link.ld"
)

add_executable(
  boot
  main.S
  print_char.S
  print_string.S
  boot.cc
)
