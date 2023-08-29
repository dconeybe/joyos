SECTIONS {
  .text : {
    *(.text)
  }
  .raw_data : {
    . = 510;
    SHORT(0xaa55);
  }
}
