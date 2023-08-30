.text
.code16

.global print_string
print_string:
movw %ax, %bx
addw $0x7c00, %bx
movb $0x0e, %ah

1:
movb (%bx), %al
cmpb $0, %al
je 1f
int $0x10
addw $1, %bx
jmp 1b
1:
ret
