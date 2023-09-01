.text
.code16

/**
 * Print a character using the BIOS.
 * The character to print must be placed in the %al register.
 * No registers are clobbered.
 */
.global joyos_print_char_asm
joyos_print_char_asm:

push %ax

movb $0x0e, %ah
int $0x10

pop %ax

ret
