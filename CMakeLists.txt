cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

project(joyos LANGUAGES C CXX ASM)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

include(JoyOsSetupCompilerWarnings)

add_subdirectory(boot)
