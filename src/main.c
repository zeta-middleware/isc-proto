/*
 * SPDX-License-Identifier: Apache-2.0
 */

#include <sys/printk.h>
#include <zephyr.h>

void main(void)
{
    printk("Hello World! %s\n", CONFIG_BOARD);
}
