#ifndef PERSISTENT_RUNTIME_173_H
#define PERSISTENT_RUNTIME_173_H
#include "persistent-runtime-168.h"
#include "persistent-diagnostic-history-173.h"

static void persistent_runtime173(void)
{
    persistent_runtime168();
    char boot[80], path[256];
    if (read_path("/proc/sys/kernel/random/boot_id",boot,sizeof(boot)) != 37 || boot[36] != '\n')
        fail("persistent diagnostic history boot");
    boot[36] = 0;
    snprintf(path,sizeof(path),"/data/.harmony-persistent166/%s",boot);
    int data = open("/data",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    int history = open(path,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    unsigned files = 0, fifos = 0;
    if (data < 0 || history < 0 || persistent173_archive(data,history,&files,&fifos) ||
        close(history) || syncfs(data) || close(data)) fail("persistent diagnostic history archive");
    dprintf(1,"PERSISTENT173_DIAGNOSTICS_ARCHIVED files=%u fifos=%u app_data_reset=0 original_launch_logic_unchanged=1\n",files,fifos);
}
#endif
