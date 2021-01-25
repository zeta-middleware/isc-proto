tui enable
set pagination on
set logging file ./build/gdb.log
set logging on

target remote localhost:2331
load "./build/zephyr/zephyr.elf"
file "./build/zephyr/zephyr.elf"
#mon reset 0

b main
c
