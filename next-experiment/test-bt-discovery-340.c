#include <stddef.h>
#include <stdio.h>
#include <assert.h>
#include "native-bt-discovery-340.h"
int main(void)
{
    unsigned char scan[]={1,0x0c,0x20,2,1,0};
    assert(bt340_command(scan,sizeof(scan))==1);
    for(size_t n=0;n<sizeof(scan);++n)assert(!bt340_command(scan,n));
    unsigned char complete[]={4,0x0e,4,1,0x0c,0x20,0};
    assert(bt340_event(complete,sizeof(complete))==1);
    unsigned char rejected[]={4,0x0f,4,0x0c,1,1,4};
    assert(bt340_event(rejected,sizeof(rejected))==1);
    unsigned char report[15]={4,0x3e,12,2,1};
    assert(bt340_event(report,sizeof(report))==2);
    for(size_t n=0;n<sizeof(report);++n)assert(!bt340_event(report,n));
    report[4]=0;assert(!bt340_event(report,sizeof(report)));
    unsigned char extended[29]={4,0x3e,26,0x0d,1};
    assert(bt340_event(extended,sizeof(extended))==2);
    extended[28]=3;assert(!bt340_event(extended,sizeof(extended)));
    unsigned char classic[18]={4,2,15,1};
    assert(bt340_event(classic,sizeof(classic))==2);
    classic[3]=2;assert(!bt340_event(classic,sizeof(classic)));
    puts("BT340_SELFTEST passed=1 classification_only=1 hardware_scan_verified=0");
    return 0;
}
