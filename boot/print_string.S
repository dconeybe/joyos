.text
.code16

/**
 * Print a null-terminated string using the BIOS.
 * The %ax register must be populated with the address of the string.
 * No registers are clobbered.
 */
.global joyos_print_string_asm
joyos_print_string_asm:

push %ax
push %bx

movw %ax, %bx
addw $0x7c00, %bx

1:
movb (%bx), %al
cmpb $0, %al
je 1f
call joyos_print_char_asm
addw $1, %bx
jmp 1b
1:

pop %bx
pop %ax
ret
