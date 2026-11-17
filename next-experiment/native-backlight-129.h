#ifndef NATIVE_BACKLIGHT_129_H
#define NATIVE_BACKLIGHT_129_H

#include "gaokun-basic-sysfs-001.h"
#include <cstdio>
#include <mutex>

#ifndef GAOKUN_BACKLIGHT_DIRECTORY
#define GAOKUN_BACKLIGHT_DIRECTORY "/sys/class/backlight/ae96000.dsi.0"
#endif

namespace NativeBacklight129 {
static std::mutex mutex;
static constexpr uint32_t maximum = 65535U;

static int32_t get(uint32_t device, uint32_t *level)
{
    if (device || !level) return PARAM;
    std::lock_guard<std::mutex> lock(mutex);
    int result = gaokun_backlight_get_range(GAOKUN_BACKLIGHT_DIRECTORY, maximum, level);
    std::fprintf(stderr, "GAOKUN_BACKLIGHT129_GET device=%u status=%d level=%u\n",
                 device, result, result ? 0U : *level);
    return result ? FAIL : OK;
}

static int32_t set(uint32_t device, uint32_t level)
{
    if (device || level > maximum) return PARAM;
    std::lock_guard<std::mutex> lock(mutex);
    int result = gaokun_backlight_set_range(GAOKUN_BACKLIGHT_DIRECTORY, maximum, level);
    std::fprintf(stderr, "GAOKUN_BACKLIGHT129_SET device=%u status=%d requested=%u\n",
                 device, result, level);
    return result ? FAIL : OK;
}
}

#endif
