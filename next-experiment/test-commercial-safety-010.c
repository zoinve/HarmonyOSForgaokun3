#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include "commercial-safety-010.h"
static void immediate(void *argument) { (void)argument; }
static void blocked(void *argument)
{
    (void)argument;
    struct timespec pause={2,0};nanosleep(&pause,NULL);
}
int main(void)
{
    const unsigned long long gib=1024ULL*1024*1024;
    assert(commercial_ram_budget010(16*gib,12*gib));
    assert(!commercial_ram_budget010(8*gib,7*gib));
    assert(!commercial_ram_budget010(16*gib,10*gib));
    assert(!commercial_ram_budget010(0,0));
    assert(commercial_bounded010(immediate,NULL,1000)==0);
    long long start=commercial_millis010();
    assert(commercial_bounded010(blocked,NULL,80)==124);
    long long elapsed=commercial_millis010()-start;
    assert(elapsed>=70 && elapsed<1000);
    puts("PASS: RAM admission rejects insufficient memory; real child timeout does not block parent");
    return 0;
}
