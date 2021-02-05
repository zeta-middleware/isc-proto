/*!
 * SPDX-License-Identifier: Apache-2.0
 */

#include <string.h>
#include <sys/crc.h>
#include <sys/printk.h>
#include <zephyr.h>
#include <zt_uart.h>
#include "kernel.h"

#define ZT_ISC_PKT_ASSERT_EQ(actual, expected, ret) \
    if (actual != expected) {                       \
        return ret;                                 \
    }

#define ZT_ISC_PKT_ASSERT(cond, ret) \
    if (!(cond)) {                   \
        return ret;                  \
    }
struct zt_isc_header_op {
    uint8_t type : 2;     /**!> 0: event, 1: command, 2: response, 3: reserved */
    uint8_t has_data : 1; /**!> 0: no data, 1: contains data */
    uint8_t cmd : 5;      /**!> 0: pub, 1: read, 2..: reserved */
    uint8_t channel : 8;  /**!> 256 channels available*/
};


struct zt_isc_header_data_info {
    uint8_t crc : 8;  /**!> CCITT 8, polynom 0x07, initial value 0x00 */
    uint8_t size : 8; /**!> data size */
};

void main(void)
{
    if (uart_open("UART_0")) {
        return;
    }

    uint8_t buffer[]                  = {10, 111, 2, 3, 4, 5, 6, 7, 8, 9};
    struct zt_isc_header_op h         = {0};
    h.type                            = 3;
    h.has_data                        = 1;
    h.cmd                             = 8;
    h.channel                         = 2;
    struct zt_isc_header_data_info hd = {0};
    hd.crc                            = crc8(buffer, sizeof(buffer), 0x07, 0x00, 0);
    hd.size                           = sizeof(buffer);

    uart_write((uint8_t *) &h, sizeof(struct zt_isc_header_op));
    uart_write((uint8_t *) &hd, sizeof(struct zt_isc_header_data_info));
    uart_write(buffer, sizeof(buffer));
    char data = 0;
    while (1) {
        if (!k_msgq_get(uart_get_input_msgq(), &data, K_FOREVER)) {
            uart_write_byte(&data);
        }
    }
}
