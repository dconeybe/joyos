.text
.code16

movb $0x0e, %ah
movw $0x7c00, %bx
movw $0, %si

1:
movb message(%bx, %si, 1), %al
cmpb $0, %al
je 1f
int $0x10
addw $1, %si
jmp 1b

1:
jmp .

message: .asciz "Hello World!"
