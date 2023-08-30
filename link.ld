SECTIONS {
  .text : {
    main.o(.text)
    EXCLUDE_FILE(main.o) *(.text)
  }
  .raw_data : AT(510) {
    SHORT(0xaa55);
  }
}
