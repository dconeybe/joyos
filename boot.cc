void joyos_print_char(char c) {
  asm volatile (
    "movb %0, %%al\n\t"
    "call joyos_print_char_asm\n\t"
    :
    : "r" (c)
    : "%ax"
  );
}

void joyos_print_string(const char* s) {
  asm volatile (
      "mov %0, %%eax\n\t"
      "call joyos_print_char_asm\n\t"
      :
      : "r" (s)
      : "%eax", "%ebx"
      );
}

static char hex_char_for_lower_4_bits(unsigned int c) {
  // TODO: Replace with a "switch" once I figure out how to correctly
  //  address into rodata.
  const unsigned int c_masked = c & 0xfU;
  if (c_masked == 0) {
    return '0';
  } else if (c_masked == 1) {
    return '1';
  } else if (c_masked == 2) {
    return '2';
  } else if (c_masked == 3) {
    return '3';
  } else if (c_masked == 4) {
    return '4';
  } else if (c_masked == 5) {
    return '5';
  } else if (c_masked == 6) {
    return '6';
  } else if (c_masked == 7) {
    return '7';
  } else if (c_masked == 8) {
    return '8';
  } else if (c_masked == 9) {
    return '9';
  } else if (c_masked == 10) {
    return 'a';
  } else if (c_masked == 11) {
    return 'b';
  } else if (c_masked == 12) {
    return 'c';
  } else if (c_masked == 13) {
    return 'd';
  } else if (c_masked == 14) {
    return 'e';
  } else if (c_masked == 15) {
    return 'f';
  } else {
    return 'X';
  }
}

static void print_hex(unsigned int c) {
  joyos_print_char('0');
  joyos_print_char('x');
  for (int shift_amt=sizeof(c)*8-4; shift_amt>=0; shift_amt-=4) {
    joyos_print_char(hex_char_for_lower_4_bits(c >> shift_amt));
  }
}

extern "C"
[[maybe_unused]] void joyos_boot() {
  print_hex(0xcafebabeU);
}
