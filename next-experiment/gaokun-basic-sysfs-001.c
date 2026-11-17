#define _POSIX_C_SOURCE 200809L
#include "gaokun-basic-sysfs-001.h"
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int attribute_path(char *path, size_t size, const char *directory,
                          const char *attribute)
{
    if (!directory || !*directory) return -EINVAL;
    int count = snprintf(path, size, "%s/%s", directory, attribute);
    return count < 0 || (size_t)count >= size ? -ENAMETOOLONG : 0;
}

static int read_text(const char *directory, const char *attribute,
                     char *text, size_t size)
{
    char path[PATH_MAX];
    int error = attribute_path(path, sizeof(path), directory, attribute);
    if (error) return error;
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -errno;
    size_t used = 0;
    for (;;) {
        ssize_t count = read(fd, text + used, size - 1 - used);
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) { error = -errno; break; }
        if (!count) break;
        used += (size_t)count;
        if (used == size - 1) { error = -EOVERFLOW; break; }
    }
    close(fd);
    if (error) return error;
    while (used && isspace((unsigned char)text[used - 1])) --used;
    text[used] = '\0';
    return used ? 0 : -ENODATA;
}

static int read_number(const char *directory, const char *attribute,
                       int64_t minimum, int64_t maximum, int64_t *result)
{
    char text[128], *end;
    int error = read_text(directory, attribute, text, sizeof(text));
    if (error) return error;
    if (!(text[0] == '-' || (text[0] >= '0' && text[0] <= '9'))) return -EINVAL;
    errno = 0;
    long long value = strtoll(text, &end, 10);
    if (errno == ERANGE || value < minimum || value > maximum) return -ERANGE;
    if (*end || end == text) return -EINVAL;
    *result = value;
    return 0;
}

int gaokun_battery_read(const char *directory, struct gaokun_battery *result)
{
    if (!result) return -EINVAL;
    memset(result, 0, sizeof(*result));
    char text[128];
    int error = read_text(directory, "type", text, sizeof(text));
    if (error) return error;
    if (strcmp(text, "Battery")) return -ENODEV;
    int64_t value;
    if (!read_number(directory, "present", 0, 1, &value)) {
        result->present = (int)value;
        result->valid |= GAOKUN_BAT_PRESENT;
    }
    if (!read_number(directory, "capacity", 0, 100, &value)) {
        result->capacity_percent = (int)value;
        result->valid |= GAOKUN_BAT_CAPACITY;
    }
    if (!read_text(directory, "status", text, sizeof(text))) {
        const char *states[] = {"Unknown", "Charging", "Discharging", "Not charging", "Full"};
        for (unsigned i = 0; i < sizeof(states) / sizeof(states[0]); ++i) {
            if (!strcmp(text, states[i])) {
                result->status = (enum gaokun_charge_state)i;
                result->valid |= GAOKUN_BAT_STATUS;
                break;
            }
        }
    }
    if (!read_number(directory, "voltage_now", 0, INT64_MAX, &result->voltage_uv))
        result->valid |= GAOKUN_BAT_VOLTAGE;
    if (!read_number(directory, "current_now", INT64_MIN, INT64_MAX, &result->current_ua))
        result->valid |= GAOKUN_BAT_CURRENT;
    if (!read_number(directory, "temp", INT64_MIN, INT64_MAX, &result->temperature_decicelsius))
        result->valid |= GAOKUN_BAT_TEMPERATURE;
    return result->valid ? 0 : -ENODATA;
}

int gaokun_backlight_get_range(const char *directory, uint32_t logical_maximum, uint32_t *level)
{
    if (!level || !logical_maximum) return -EINVAL;
    int64_t maximum, brightness;
    int error = read_number(directory, "max_brightness", 1, UINT32_MAX, &maximum);
    if (error) return error;
    error = read_number(directory, "brightness", 0, maximum, &brightness);
    if (error) return error;
    *level = (uint32_t)(((uint64_t)brightness * logical_maximum + (uint64_t)maximum / 2U) / (uint64_t)maximum);
    return 0;
}

int gaokun_backlight_set_range(const char *directory, uint32_t logical_maximum, uint32_t level)
{
    if (!logical_maximum) return -EINVAL;
    if (level > logical_maximum) return -ERANGE;
    int64_t maximum;
    int error = read_number(directory, "max_brightness", 1, UINT32_MAX, &maximum);
    if (error) return error;
    uint32_t hardware = (uint32_t)(((uint64_t)level * (uint64_t)maximum + logical_maximum / 2U) / logical_maximum);
    char path[PATH_MAX], text[32];
    error = attribute_path(path, sizeof(path), directory, "brightness");
    if (error) return error;
    int count = snprintf(text, sizeof(text), "%u\n", hardware);
    int fd = open(path, O_WRONLY | O_CLOEXEC);
    if (fd < 0) return -errno;
    ssize_t written;
    do { written = write(fd, text, (size_t)count); } while (written < 0 && errno == EINTR);
    error = written < 0 ? -errno : written == count ? 0 : -EIO;
    if (close(fd) && !error) error = -errno;
    return error;
}

int gaokun_backlight_get(const char *directory, uint32_t *level)
{
    return gaokun_backlight_get_range(directory, 255U, level);
}

int gaokun_backlight_set(const char *directory, uint32_t level)
{
    return gaokun_backlight_set_range(directory, 255U, level);
}
