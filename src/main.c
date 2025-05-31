/**
 * @file main.c
 * @brief CRSF to PWM converter implementation for STC15F104W microcontroller
 *
 * This file implements a CRSF (Crossfire) to PWM signal converter using STC15 microcontroller.
 * It receives CRSF protocol data through UART and converts it to PWM signals for RC servos.
 *
 * @author Chagin O.S.
 * @date 2025.05.29
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

static uint8_t input_buffer[PACKAGE_MAX_SIZE];
static uint16_t channel_us[EVENT_COUNT] = {992, 992, 992, 992, 992, 14600};
static state_flags_t flags = {0};
static uint8_t Serial_Data = 0;

inline void Uart1_Init(void) // 115200bps@22.1184MHz
{
    INT_CLKO |= 0x40; // Enable Int4 Falling mode
    AUXR |= 0x04;     // Timer clock is 1T mode
    IE2 |= 0x04;      // Enable Interrupt for Timer2
}

inline void Timer0_Init(void) // ~0.5425us@22.1184MHz
{
    AUXR &= 0x7F; // Timer clock is 12T mode
    TMOD &= 0xF0; // Mode 0/1 (presumably Mode 1: 16-bit)
    TF0 = 0;      // Clear Timer0 Overflow flag
    TR0 = 1;      // Start Timer0
    ET0 = 1;      // Enable Timer0 interrupt
}

inline void Port3_Init(void)
{
    P3M0 = 0x00;
    P3M1 = 0x00;
}

void main(void)
{
    uint8_t byte;
    uint8_t index = 0;
    uint8_t crc = 0;
    uint8_t length = 0;
    uint8_t type = 0;

    Uart1_Init();
    Timer0_Init();
    Port3_Init();

    ENABLE_INTERRUPTS();

    while (1)
    {
        if (flags.Receive_Interrupt)
        {
            DISABLE_INTERRUPTS();
            flags.Receive_Interrupt = 0;
            byte = Serial_Data;
            ENABLE_INTERRUPTS();

            switch (flags.state)
            {
            case WAIT_SYNC:
                if (byte == 0xC8)
                    flags.state = WAIT_LENGTH;
                break;

            case WAIT_LENGTH:
                if (byte < 2 || byte > 62)
                {
                    flags.state = WAIT_SYNC;
                    break;
                }
                length = byte;
                crc = 0;
                flags.state = WAIT_TYPE;
                break;

            case WAIT_TYPE:
                type = byte;
                index = 0;
                flags.state = WAIT_PAYLOAD;
                break;

            case WAIT_PAYLOAD:
                if (index >= PACKAGE_MAX_SIZE)
                {
                    flags.state = WAIT_SYNC;
                    break;
                }
                input_buffer[index++] = byte;
                if (index >= length - 1)
                    flags.state = WAIT_CRC;
                break;

            case WAIT_CRC:
                if (crc == byte && type == CRSF_FRAMETYPE_CHANNELS)
                {
                    DISABLE_INTERRUPTS();
                    channel_us[0] = ((crsf_channels_t *)input_buffer)->ch0;
                    channel_us[1] = ((crsf_channels_t *)input_buffer)->ch1;
                    channel_us[2] = ((crsf_channels_t *)input_buffer)->ch2;
                    channel_us[3] = ((crsf_channels_t *)input_buffer)->ch3;
                    channel_us[4] = ((crsf_channels_t *)input_buffer)->ch4;
                    channel_us[5] = 14600; // TODO: Incorrect value
                    for (uint8_t i = 0; i < CHANNEL_COUNT; i++)
                    {
                        if (channel_us[i] < 172 || channel_us[i] > 1811)
                            channel_us[i] = 992;
                        channel_us[5] -= 992 - channel_us[i];
                    }
                    ENABLE_INTERRUPTS();
                }
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
    static uint8_t current_channel = 0;
    uint16_t ticks = (0xFB1E) - channel_us[current_channel] * 3 / 2;
    TH0 = ticks >> 8, TL0 = ticks >> 0;

    if (current_channel == 0)
        P31 = 1;
    else if (current_channel == 1)
        P31 = 0, P32 = 1;
    else if (current_channel == 2)
        P32 = 0, P33 = 1;
    else if (current_channel == 3)
        P33 = 0, P34 = 1;
    else if (current_channel == 4)
        P34 = 0, P35 = 1;
    else if (current_channel == 5)
        P35 = 0, current_channel = 0xFF;

    ++current_channel;
}

void Timer2_Isr(void) __interrupt(12)
{
    static uint8_t rx_buf = 0, rx_cnt = 0;
    rx_buf |= (P30 ? 1 : 0) << (rx_cnt++);

    if (rx_cnt >= 8)
    {
        Serial_Data = rx_buf;
        rx_buf = 0, rx_cnt = 0;
        flags.Receive_Interrupt = 1;
        INT_CLKO |= 0x40; // Enable Int4
        AUXR &= ~0x10;    // Disable Timer2
        T2H = 0xFF, T2L = 0xFF;
    }
}

void INT4_ISR(void) __interrupt(16)
{
    INT_CLKO &= ~0x40; // Disable Int4
    T2H = T2H_INIT, T2L = T2L_INIT;
    AUXR |= 0x10; // Enable Timer 2
}