#ifndef CRSF_H
#define CRSF_H

#include <stdint.h>

// Размеры и константы
#define PACKAGE_MAX_SIZE (32)           // Максимальный размер пакета
#define CHANNEL_COUNT (5)               // Количество каналов
#define EVENT_COUNT (CHANNEL_COUNT + 1) // Количество событий
#define CRSF_FRAMETYPE_CHANNELS (0x16)  // Тип фрейма каналов

// -----------------------------------------------------------------------------

// T0_RELOAD = 65536 - FOSC/3/BAUDRATE/M (1T:M=1; 12T:M=12)
// NOTE: (FOSC/3/BAUDRATE) must be greater then 98, (RECOMMEND GREATER THEN 110)
#define T0_RELOAD (0x10000 - FOSC / BAUDRATE / 3) // 115200bps @ 33.1776MHz
#define RX_pin P30

// -----------------------------------------------------------------------------

#define US_TO_TICK(us) ((us) * FOSC / 1000000UL / 12) // 2,7648 мкс на 1 тик

#define CRSF_ADD (2163)
#define CRSF_MIN (172)  // 62  мкс //  Минимальное значение ШИМ
#define CRSF_MID (992)  // 358 мкс // Середина. Должно соответствовать 1500мкс
#define CRSF_MAX (1811) // 655 мкс // Максимальное значение ШИМ

#define PWM_MID_US 1500                       // us -> ~ 830 тиков
#define PWM_MID_TICK (US_TO_TICK(PWM_MID_US)) // ~ 830 тиков

// #define BASE (uint16_t)(0x10000 - TICKS_US(PWM_MID_US) - CRSF_MID)
// #define SIGNAL ((CHANNEL_COUNT - 1) * (BASE + 2 * CRSF_MID))
// #define FRAME (uint16_t)(TICKS_US(20000))
// #define FILLER (uint16_t)(FRAME - SIGNAL)

// Полный период в 20мс равен (0x10000 - 0xD800)
// минимум  1000 -> US_TO_TICK(1000) = 2764
// средний  1500 -> US_TO_TICK(1500) = 4147
// максимум 2000 -> US_TO_TICK(2000) = 5529

// максимальный диапазон сигнала от 172 до 1811 = 1639 отсчетов или 592мкс
// получается, что он ровно в 2 раза меньше нужного => умножаем его на 2:
//   - 172 --> 344  тиков --> 124
//   - 992 --> 1984 тиков --> 717
//   -1811 --> 3622 тиков --> 1310
// при этом 992 тика должны соответствовать 1500мкс.
// Для этого вычисляем дополнительную прибавку CRSF_ADD: 4147-992*2 = 2163 тиков
// И проверяем:
//   - 172 --> 2163 + 344  --> 2507 тиков --> 906мкс
//   - 992 --> 2163 + 1984 --> 4147 тиков --> 1499мкс
//   -1811 --> 2163 + 3622 --> 5785 тиков --> 2092мкс
// Дальше остается только составить преобразование. Полный счетчик 0x10000 тиков
// Соответственно:
#define CRSF_TO_TIMER(CRSF_VAL) (0x10000 - CRSF_ADD - (CRSF_VAL << 1))
// Остается рассчитать отработанный остаток. Для этого из полного периода в 20мс
// нужно вычесть времена остальных каналов.
//   - 20мс --> US_TO_TICK(20000) --> 55296 тиков - (значения каждого канала *2)
#define PWM_PERIOD_US (20000)
#define PWM_PERIOD_TICK (US_TO_TICK(PWM_PERIOD_US))

// -----------------------------------------------------------------------------

// Состояния разбора входящего пакета
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
    crsf_state_t state;        // Состояние
    uint8_t package_reading;   // Флаг чтения пакета
    uint8_t channels_read;     // Флаг чтения каналов
    uint8_t Receive_Interrupt; // Флаг прерывания приема
    uint8_t REND;              // Состояние передачи
    uint8_t RBUF;              // Новый байт
} state_flags_t;

#endif // CRSF_H