#include <string.h>
static int is_oobe_target(const char *name) {
    return strcmp(name, "com.huawei.hmos.hwstartupguide") == 0;
}
