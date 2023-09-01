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

add_link_options(
  "${common_compiler_flags}"
  "LINKER:--oformat=binary"
  "LINKER:SHELL:-T ${CMAKE_CURRENT_LIST_DIR}/link.ld"
)

add_executable(
  joyos_boot
  main.S
  print_char.S
  print_string.S
)
