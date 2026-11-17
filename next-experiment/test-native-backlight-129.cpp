#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <string>

static constexpr int OK = 0, FAIL = -1, PARAM = -3;
static char directory[] = "/tmp/gaokun-backlight-129-XXXXXX";
#define GAOKUN_BACKLIGHT_DIRECTORY directory
#include "native-backlight-129.h"

static void attribute(const char *name, const char *value)
{
    std::ofstream stream(std::string(directory) + "/" + name);
    stream << value << '\n';
    assert(stream.good());
}

int main()
{
    assert(mkdtemp(directory));
    attribute("max_brightness", "4095");
    attribute("brightness", "204");
    uint32_t level = 99;
    assert(NativeBacklight129::get(1, &level) == PARAM);
    assert(NativeBacklight129::get(0, nullptr) == PARAM);
    assert(NativeBacklight129::set(1, 1) == PARAM);
    assert(NativeBacklight129::set(0, 65536) == PARAM);
    assert(NativeBacklight129::set(0, 11363) == OK);
    assert(NativeBacklight129::get(0, &level) == OK && level == 11363);
    attribute("max_brightness", "invalid");
    assert(NativeBacklight129::get(0, &level) == FAIL);
    assert(NativeBacklight129::set(0, 100) == FAIL);
    attribute("max_brightness", "4095");
    std::filesystem::remove(std::string(directory) + "/brightness");
    assert(NativeBacklight129::get(0, &level) == FAIL);
    assert(NativeBacklight129::set(0, 100) == FAIL);
    assert(!std::filesystem::exists(std::string(directory) + "/brightness"));
    std::filesystem::remove(std::string(directory) + "/max_brightness");
    std::filesystem::remove(directory);
    return 0;
}
