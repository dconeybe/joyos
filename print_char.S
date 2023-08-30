.text
.code16

/**
 * Print a character using the BIOS.
 * The character to print must be placed in the %al register.
 * The %ah register is clobbered by this function.
 */
.global print_char
print_char:

movb $0x0e, %ah
int $0x10
ret
