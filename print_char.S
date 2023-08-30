.text
.code16

/**
 * Print a character using the BIOS.
 * The character to print must be placed in the %al register.
 * The %ah register is clobbered by this function.
 */
.global joyos_print_char_asm
joyos_print_char_asm:

movb $0x0e, %ah
int $0x10
ret
