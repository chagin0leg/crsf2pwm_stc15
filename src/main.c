/**
 * @file main.c
 * @brief CRSF to PWM converter implementation for STC15F104W microcontroller
 *
 * This file implements a CRSF (Crossfire) to PWM signal converter using STC15 microcontroller.
 * It receives CRSF protocol data through UART and converts it to PWM signals for RC servos.
 *
 * @author Chagin O.S.
 * @date 2025.06.03
 * @version 1.0
 *
 * @details
 * The converter supports up to 5 PWM channels with the following features:
 * - CRSF protocol reception at 115200 baud rate
 * - PWM signal generation with configurable pulse width
 * - Input signal validation and failsafe handling
 * - Timer-based precise timing control
 */

#include <stdint.h>
#include "stc15.h"
#include "crsf.h"

uint8_t input_buffer[PACKAGE_MAX_SIZE];
uint16_t channel_us[EVENT_COUNT] = {
    CRSF_TO_TIMER(CRSF_MID),
    CRSF_TO_TIMER(CRSF_MID),
    CRSF_TO_TIMER(CRSF_MID),
    CRSF_TO_TIMER(CRSF_MID),
    CRSF_TO_TIMER(CRSF_MID),
    0x10000 - 0xD800 + (CRSF_ADD + (CRSF_MID * 2)) * CHANNEL_COUNT,
};
state_flags_t flags = {0};

inline void Uart1_Init(void) // 115200bps@33.1776MHz
{
    TMOD = 0x00;            // Timer0 in 16-bit auto reload mode
    AUXR = 0x80;            // Timer0 working at 1T mode
    TL0 = T0_RELOAD & 0xFF; // Initial Timer0 and set reload value
    TH0 = T0_RELOAD >> 8;   // Initial Timer0 and set reload value
    TR0 = 1;                // Timer0 start running
    ET0 = 1;                // Enable Timer0 interrupt
    PT0 = 1;                // Improve Timer0 interrupt priority
}

inline void Timer2_Init(void) // ~0.3617us@33.1776MHz
{
    IE2 |= 0x04;  // Enable timer2 interrupt
    AUXR |= 0x10; // Enable PCA clock
    EA = 1;       // Enable interrupts
}

// Initializes the GPIO ports for PWM signal output and UART data input
inline void GPIO_Init(void)
{
    P3M0 = 0x3e; // Set push-pull mode for P31 .. P35 (PWM channels)
    P3M1 = 0x01; // Set input-only mode for P30 (UART RX)
}

inline void unpack(const uint8_t *data, uint16_t *out_values)
{
    uint32_t bit_buffer = 0;
    uint8_t bit_count = 0;
    uint8_t value_index = 0;
    uint16_t value, offset;
    offset = (0x10000 - 0xD800 + CRSF_ADD * CHANNEL_COUNT);

    while (value_index < CHANNEL_COUNT)
    {
        bit_buffer |= ((uint32_t)(*data++)) << bit_count;
        bit_count += 8;

        if (bit_count >= 11)
        {
            value = (bit_buffer & ((1 << 11) - 1)) << 1;
            out_values[value_index++] = 0x10000 - CRSF_ADD - value;
            offset += value;
            bit_buffer >>= 11;
            bit_count -= 11;
        }
    }
    out_values[CHANNEL_COUNT] = offset;
}

void main(void)
{
    uint8_t byte = 0;
    uint8_t index = 0;
    uint8_t crc = 0;
    uint8_t length = 0;
    uint8_t type = 0;

    GPIO_Init();
    Uart1_Init();
    Timer2_Init();

    while (1)
    {

        if (flags.REND)
        {
            flags.REND = 0;
            byte = flags.RBUF;

            switch (flags.state)
            {
            case WAIT_SYNC:
                if (byte == 0xC8)
                    flags.state = WAIT_LENGTH;
                break;

            case WAIT_LENGTH:
                if (byte < 22 || byte > PACKAGE_MAX_SIZE)
                {
                    flags.state = WAIT_SYNC;
                    break;
                }
                length = byte - 2;
                flags.state = WAIT_TYPE;
                break;

            case WAIT_TYPE:
                type = byte;
                index = crc = 0;
                flags.state = WAIT_PAYLOAD;
                break;

            case WAIT_PAYLOAD:
                if (index >= PACKAGE_MAX_SIZE)
                {
                    flags.state = WAIT_SYNC;
                    break;
                }
                input_buffer[index++] = byte;
                if (index >= length)
                    flags.state = WAIT_CRC;
                break;

            case WAIT_CRC:
                if (crc == byte && type == CRSF_FRAMETYPE_CHANNELS)
                    unpack(input_buffer, channel_us);
                flags.state = WAIT_SYNC;
                break;
            }

            crc ^= byte;
            for (uint8_t i = 0; i < 8; i++)
                crc = (crc & 0x80) ? (crc << 1) ^ 0xD5 : (crc << 1);
        }
    }
}

void Timer0_ISR(void) __interrupt(1)
{
    static uint8_t RCNT = 0, RBIT = 0, RDAT = 0, RING = 0;

    if (RING)
    {
        if (--RCNT == 0)
        {
            RCNT = 3; // reset send baudrate counter
            if (--RBIT == 0)
            {
                flags.RBUF = RDAT; // save the data to flags.RBUF
                RING = 0;          // stop receive
                flags.REND = 1;    // set receive completed flag
            }
            else
            {
                RDAT >>= 1;
                if (RX_pin)
                    RDAT |= 0x80; // shift RX data to RX buffer
            }
        }
    }
    else if (!RX_pin)
    {
        RING = 1; // set start receive flag
        RCNT = 4; // initial receive baudrate counter
        RBIT = 9; // initial receive bit number (8 data bits + 1 stop bit)
    }
}

void Timer2_Isr(void) __interrupt(12)
{
    static uint8_t channel = 0;
    T2H = (uint8_t)(channel_us[channel] >> 8);
    T2L = (uint8_t)(channel_us[channel] >> 0);
    P3 &= ~(0b00111110);
    if (channel != 0)
        P3 |= 0b00000001 << channel;
    if (++channel > 5)
        channel = 0;
}
