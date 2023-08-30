.text
.code16

.global print_string
print_string:

movw %ax, %bx
addw $0x7c00, %bx

1:
movb (%bx), %al
cmpb $0, %al
je 1f
call print_char
addw $1, %bx
jmp 1b
1:
ret
