int gval = 4;

int main() {
  asm volatile (
    "mov $0x0e, %%ah\n"
    "mov $0x48, %%al\n"
    "int $0x10\n"
    :
    :
    : "%eax"
  );
}
