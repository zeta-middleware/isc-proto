#!/usr/bin/sh
west debugserver &
arm-zephyr-eabi-gdb -x debug.gdb
