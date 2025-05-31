#ifndef CRSF_H
#define CRSF_H

#include <stdint.h>

// Размеры и константы
#define PACKAGE_MAX_SIZE (64)           // Максимальный размер пакета
#define CHANNEL_COUNT (5)               // Количество каналов
#define EVENT_COUNT (CHANNEL_COUNT + 1) // Количество событий
#define CRSF_FRAMETYPE_CHANNELS 0x16    // Тип фрейма каналов

// Управление прерываниями
#define DISABLE_INTERRUPTS() EA = 0 // Отключение прерываний
#define ENABLE_INTERRUPTS() EA = 1  // Включение прерываний
// #define Receive_Interrupt RI        // Прерывание приема
// #define Serial_Data SBUF            // Буфер приема

#define TIMER2_RELOAD (0xFFFF - 192)           // 192 = 22.1184MHz/115200
#define T2H_INIT ((TIMER2_RELOAD >> 8) & 0xFF) // 0xFF
#define T2L_INIT (TIMER2_RELOAD & 0xFF)        // 0x40

// Структура каналов
typedef struct PACKED
{
    uint16_t ch0 : 11;
    uint16_t ch1 : 11;
    uint16_t ch2 : 11;
    uint16_t ch3 : 11;
    uint16_t ch4 : 11;
    uint16_t ch5 : 11;
    uint16_t ch6 : 11;
    uint16_t ch7 : 11;
    uint16_t ch8 : 11;
    uint16_t ch9 : 11;
    uint16_t ch10 : 11;
    uint16_t ch11 : 11;
    uint16_t ch12 : 11;
    uint16_t ch13 : 11;
    uint16_t ch14 : 11;
    uint16_t ch15 : 11;
} crsf_channels_t;

// Состояния state machine
typedef enum
{
    WAIT_SYNC,    // Ожидание синхронизации
    WAIT_LENGTH,  // Ожидание длины
    WAIT_TYPE,    // Ожидание типа
    WAIT_PAYLOAD, // Ожидание данных
    WAIT_CRC      // Ожидание CRC
} crsf_state_t;

// Флаги состояния
typedef struct
{
    crsf_state_t state : 3;        // Состояние
    uint8_t package_reading : 1;   // Флаг чтения пакета
    uint8_t channels_read : 1;     // Флаг чтения каналов
    uint8_t Receive_Interrupt : 1; // Флаг прерывания приема
    uint8_t reserved : 2;          // Состояние передачи
} state_flags_t;

#endif // CRSF_H