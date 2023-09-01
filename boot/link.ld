SECTIONS {
  .text : {
    *(*.joyos_boot_entry_section)
    *(*.text)
  }
  .raw_data : AT(510) {
    SHORT(0xaa55);
  }
  /DISCARD/ : {
    *(*)
  }
}
