boot: main.o print_string.o link.ld
	g++ main.o print_string.o -o boot -fno-exceptions -fno-rtti -T link.ld -Wl,--oformat=binary -nostartfiles -nostdlib

main.o: main.S
	g++ -c main.S -o main.o -fno-exceptions -fno-rtti -nostartfiles -nostdlib

print_string.o: print_string.S
	g++ -c print_string.S -o print_string.o -fno-exceptions -fno-rtti -nostartfiles -nostdlib

.PHONY: clean
clean:
	rm -f boot main.o print_string.o
