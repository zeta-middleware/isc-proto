/*
 * SPDX-License-Identifier: Apache-2.0
 */

#include <string.h>
#include <sys/crc.h>
#include <sys/printk.h>
#include <zephyr.h>
#include <zt_uart.h>

#define ZT_ISC_PKT_ASSERT_EQ(actual, expected, ret) \
    if (actual != expected) {                       \
        return ret;                                 \
    }

#define ZT_ISC_PKT_ASSERT(cond, ret) \
    if (!(cond)) {                   \
        return ret;                  \
    }

struct zt_isc_header {
    uint8_t type : 2;    /**!> 0: event, 1: command, 2: response, 3: reserved */
    uint8_t cmd : 6;     /**!> 0: pub, 1: read, 2..: reserved */
    uint8_t channel : 8; /**!> 256 channels available*/
    uint8_t crc : 8;     /**!> CCITT 8 */
};

void main(void)
{
    if (uart_open("UART_0")) {
        printk("Could not configure UART\n");
    }
    printk("Board: %s\n", CONFIG_BOARD);
    uint8_t buffer[]       = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    struct zt_isc_header h = {0};
    h.type                 = 0;
    h.cmd                  = 0;
    h.channel              = 5;
    h.crc                  = crc8(buffer, sizeof(buffer), 0xFF, buffer[0], 0);

    uart_write((uint8_t *) &h, sizeof(struct zt_isc_header));
    uart_write(buffer, sizeof(buffer));
    char c = 't';
    uart_write_byte(&c);
    char data = 0;
    while (1) {
        if (!k_msgq_get(uart_get_input_msgq(), &data, K_FOREVER)) {
            uart_write_byte(&data);
        }
    }
}
