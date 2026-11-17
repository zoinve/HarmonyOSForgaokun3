/* Ubuntu-only network fixture. This does not run or authenticate HarmonyOS. */
#define _GNU_SOURCE
#include "live-debug-discovery-159.h"
#include <stdlib.h>

int main(int argc, char **argv)
{
    if (argc != 3 || strcmp(argv[1],"--ubuntu-fixture") ||
        strcmp(argv[2],"192.168.10.128") || geteuid()) return 77;
    unsigned index = if_nametoindex("wlP6p1s0");
    int fd = discovery159_open("wlP6p1s0");
    if (fd < 0 || !index) return 78;
    puts("UBUNTU_ONLY_DISCOVERY159_READY lifetime_seconds=15 authentication_not_proved=1");
    fflush(stdout);
    struct timespec start, now;
    if (clock_gettime(CLOCK_MONOTONIC,&start)) return 79;
    unsigned remaining = 16, replies = 0;
    time_t last_reply = 0;
    for (;;) {
        if (clock_gettime(CLOCK_MONOTONIC,&now)) return 79;
        if (now.tv_sec - start.tv_sec >= 15) break;
        struct pollfd item = {.fd=fd,.events=POLLIN};
        if (poll(&item,1,100) > 0) {
            int result = discovery159_step(fd,index,argv[2],&remaining,&last_reply);
            if (result < 0) { close(fd); return 80; }
            replies += (unsigned)result;
        }
    }
    close(fd);
    printf("UBUNTU_ONLY_DISCOVERY159_STOP replies=%u listener_closed=1\n",replies);
    return 0;
}
