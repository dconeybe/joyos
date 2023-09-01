# Use a custom section so that the linker script can refer to this section and
# place it at offset 0 in the produced binary. All this section does is jump
# into the .text section at the point where the code actually starts.
.section .joyos_boot_entry_section, "ax"
.code16

jmp 1f

.text
.code16
1:
movw $0x8000, %bp
movw $0x8000, %sp

movw $.LHelloWorld, %ax
call joyos_print_string_asm
movw $.LGoodbyeWorld, %ax
call joyos_print_string_asm
hlt

.text
.LHelloWorld: .asciz "Hello World!"
.LGoodbyeWorld: .asciz "Goodbye World :("
