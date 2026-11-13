#include <assert.h>
#include "oobe-target.h"
int main(void) {
    assert(is_oobe_target("com.huawei.hmos.hwstartupguide"));
    assert(!is_oobe_target("com.huawei.hmos.hwstartupguide.extra"));
    assert(!is_oobe_target("ohos.sceneboard"));
    assert(!is_oobe_target("/system/bin/sh"));
    assert(!is_oobe_target(""));
    return 0;
}
