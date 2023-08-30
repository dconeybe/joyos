.text
.code16

movw $0x8000, %bp
movw $0x8000, %sp

movw $message1, %ax
call print_message
movw $message2, %ax
call print_message
jmp .

print_message:
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

message1: .asciz "Hello World!"
message2: .asciz "Goodbye World :("
