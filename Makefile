boot: boot.cc link.ld
	g++ boot.cc -o boot -fno-exceptions -fno-rtti -T link.ld -Wl,--entry=main -Wl,--oformat=binary -nostartfiles -nostdlib
