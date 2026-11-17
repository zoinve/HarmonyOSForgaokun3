#ifndef GAOKUN_BASIC_SYSFS_001_H
#define GAOKUN_BASIC_SYSFS_001_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum gaokun_charge_state {
    GAOKUN_CHARGE_UNKNOWN,
    GAOKUN_CHARGING,
    GAOKUN_DISCHARGING,
    GAOKUN_NOT_CHARGING,
    GAOKUN_FULL
};

enum gaokun_battery_fields {
    GAOKUN_BAT_PRESENT = 1U << 0,
    GAOKUN_BAT_CAPACITY = 1U << 1,
    GAOKUN_BAT_STATUS = 1U << 2,
    GAOKUN_BAT_VOLTAGE = 1U << 3,
    GAOKUN_BAT_CURRENT = 1U << 4,
    GAOKUN_BAT_TEMPERATURE = 1U << 5
};

struct gaokun_battery {
    uint32_t valid;
    int present;
    int capacity_percent;
    enum gaokun_charge_state status;
    int64_t voltage_uv;
    int64_t current_ua;
    int64_t temperature_decicelsius;
};

/* Paths name existing sysfs device directories, not synthetic service state. */
int gaokun_battery_read(const char *directory, struct gaokun_battery *result);
int gaokun_backlight_get(const char *directory, uint32_t *level);
int gaokun_backlight_set(const char *directory, uint32_t level);
int gaokun_backlight_get_range(const char *directory, uint32_t logical_maximum, uint32_t *level);
int gaokun_backlight_set_range(const char *directory, uint32_t logical_maximum, uint32_t level);

#ifdef __cplusplus
}
#endif

#endif
