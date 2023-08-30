.text
.code16

movw $0x8000, %bp
movw $0x8000, %sp

movw $message1, %ax
call print_string
movw $message2, %ax
call print_string
jmp .

message1: .asciz "Hello World!"
message2: .asciz "Goodbye World :("
