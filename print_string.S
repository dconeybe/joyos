.text
.code16

.global joyos_print_string_asm
joyos_print_string_asm:

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
ret
