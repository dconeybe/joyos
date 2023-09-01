.text
.code16

movw $0x8000, %bp
movw $0x8000, %sp

movw $42f, %ax
call joyos_print_string_asm
movw $43f, %ax
call joyos_print_string_asm
jmp .

42: .asciz "Hello World!"
43: .asciz "Goodbye World :("
