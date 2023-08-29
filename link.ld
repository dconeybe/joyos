SECTIONS {
  .text : {
    *(.text)
  }
  .raw_data : AT(510) {
    SHORT(0xaa55);
  }
}
