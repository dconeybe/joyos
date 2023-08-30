boot: boot.S link.ld
	g++ boot.S -o boot -fno-exceptions -fno-rtti -T link.ld -Wl,--oformat=binary -nostartfiles -nostdlib
