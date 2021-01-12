/*
 * SPDX-License-Identifier: Apache-2.0
 */

#include <sys/printk.h>
#include <tinycbor/cbor.h>
#include <tinycbor/cbor_buf_writer.h>
#include <zephyr.h>

#define ZT_ISC_PKT_ASSERT(actual, expected, ret)             \
    if (actual != expected) {                                \
        printk("Error line: %d, code %d", __LINE__, actual); \
        return ret;                                          \
    }

void decode()
{
    // CborParser parser;
    // CborValue data_val, pkt_list_val;
}

struct zt_isc_packet {
    uint8_t id;
};

typedef struct zt_isc_packet zt_isc_packet_t;


int zt_isc_packet_encode(zt_isc_packet_t* pkt, uint8_t* buffer_x, size_t buffer_size,
                         size_t* buffer_length)
{
    // ZT_ISC_PKT_ASSERT(pkt != NULL, -ENODEV);
    // ZT_ISC_PKT_ASSERT(buffer_x != NULL, -ENOBUFS);
    // ZT_ISC_PKT_ASSERT(buffer_size > 0, -ENOMEM);
    uint8_t buffer[128] = {0};
    uint8_t data[]      = "hello\n";
    CborEncoder encoder;
    CborEncoder data_enc;
    struct cbor_buf_writer bwriter = {0};
    cbor_buf_writer_init((struct cbor_buf_writer*) &bwriter, buffer, 128);
    cbor_encoder_init(&encoder, (cbor_encoder_writer*) &bwriter, 0);
    ZT_ISC_PKT_ASSERT(cbor_encoder_create_array(&encoder, &data_enc, 3), CborNoError,
                      -EBADF);
    ZT_ISC_PKT_ASSERT(cbor_encode_int(&data_enc, 0xffffffff), CborNoError, -ENODATA);
    ZT_ISC_PKT_ASSERT(cbor_encode_int(&data_enc, 2), CborNoError, -ENODATA);
    ZT_ISC_PKT_ASSERT(cbor_encode_byte_string(&data_enc, data, sizeof(data)), CborNoError,
                      -ENOMEM);  // 010.00011 -> 43
    ZT_ISC_PKT_ASSERT(cbor_encoder_close_container(&encoder, &data_enc), CborNoError,
                      -ENOBUFS);
    *buffer_length = bwriter.enc.bytes_written;
    printk("Encoded data:\n");
    printk("Size: %d\n", *buffer_length);
    for (int i = 0; i < *buffer_length; ++i) {
        printk("%02X", buffer[i]);
    }
    printk("\n");
    return 0;
}


// void encode_2b(unsigned short *src, char *dst)
// {
//     for (int i = 0; i < 4; i++) {
//         dst[i] = (*src >> (i * 4)) & 0x0F;
//         if (0 <= dst[i] && dst[i] <= 9) {
//             dst[i] += 48; /* 48 + 0 is '0' */
//         } else if (10 <= dst[i] && dst[i] <= 15) {
//             dst[i] += 55; /* 55 + 10 is 'A' */
//         }
//     }
// }

// void decode_2b(char *src, unsigned short *dst)
// {
//     char temp = 0;
//     for (int i = 0; i < 4; i++) {
//         temp = src[i];
//         if (48 <= temp && temp <= 57) {
//             temp -= 48; /* '0' - 48 is 0 */
//         } else if (65 <= temp && temp <= 80) {
//             temp -= 55; /* 'A'(65) - 55 is 10 */
//         } else if (97 <= temp && temp <= 112) {
//             temp -= 87; /* 'a'(97) - 87 is 10 */
//         }
//         *dst |= temp << (4 * i);
//     }
// }

void main(void)
{
    printk("Hello World! %s\n", CONFIG_BOARD);
    size_t buf_size = 0;
    printk("%d\n", zt_isc_packet_encode(0, 0, 0, &buf_size));
}
