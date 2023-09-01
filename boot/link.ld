SECTIONS {
  .text : {
    ${MAIN_O_PATH}(*.text)
    EXCLUDE_FILE(${MAIN_O_PATH}) *(.text)
  }
  .raw_data : AT(510) {
    SHORT(0xaa55);
    SHORT(0xaa55);
  }
  /DISCARD/ : {
      *(*)
  }
}
