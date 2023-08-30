SECTIONS {
  .text : {
    CMakeFiles/boot.dir/main.S.o(*.text)
    EXCLUDE_FILE(CMakeFiles/boot.dir/main.S.o) *(.text)
  }
  .data : {
    *(.data)
  }
  .bss : {
    *(.bss)
  }
  .raw_data : AT(510) {
    SHORT(0xaa55);
  }
  /DISCARD/ : {
      *(*)
  }
}
