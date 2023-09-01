# Flags that are specified to the compiler driver both when compiling and when linking.
set(
  common_compiler_flags
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

add_compile_options("${common_compiler_flags}")

# Put main.S in its own library so that its output file can be determined
# and injected into the linker script, which needs to know the output file
# to ensure that it occurs at byte 0 in the resulting binary.
add_library(
  joyos_boot_main
  OBJECT
  main.S
)

add_link_options(
  "${common_compiler_flags}"
  LINKER:--oformat=binary
  "LINKER:SHELL:-T ${CMAKE_CURRENT_BINARY_DIR}/link.$<CONFIG>.ld"
)

# Generate a linker script that ensures that the text section of main.S
# occurs at byte 0 of the generated binary. The `link.ld` file in this
# directory is used verbatim, but its ${MAIN_O_PATH} is replaced with the
# path to the compiled artifact from compiling main.S just as it is specified
# to the compiler driver.
add_custom_command(
  OUTPUT
    ${CMAKE_CURRENT_BINARY_DIR}/link.$<CONFIG>.ld
  COMMAND 
    "${CMAKE_COMMAND}"
    "-DSRC_FILE:FILEPATH=${CMAKE_CURRENT_LIST_DIR}/link.ld"
    "-DDEST_FILE:FILEPATH=${CMAKE_CURRENT_BINARY_DIR}/link.$<CONFIG>.ld"
    "-DMAIN_O_PATH:STRING=$<PATH:RELATIVE_PATH,$<PATH:NORMAL_PATH,$<TARGET_OBJECTS:joyos_boot_main>>,${CMAKE_BINARY_DIR}>"
    -P "${CMAKE_CURRENT_LIST_DIR}/generate_link_ld.cmake"
  MAIN_DEPENDENCY
    link.ld
  DEPENDS
    generate_link_ld.cmake
  COMMENT
    "Generating ${CMAKE_CURRENT_BINARY_DIR}/link.$<CONFIG>.ld from ${CMAKE_CURRENT_LIST_DIR}/link.ld"
)

add_custom_target(
  joyos_boot_link_ld
  DEPENDS
    ${CMAKE_CURRENT_BINARY_DIR}/link.$<CONFIG>.ld
)

add_executable(
  joyos_boot
  $<TARGET_OBJECTS:joyos_boot_main>
  print_char.S
  print_string.S
  ${CMAKE_CURRENT_BINARY_DIR}/link.$<CONFIG>.ld
)

add_dependencies(joyos_boot joyos_boot_link_ld)
