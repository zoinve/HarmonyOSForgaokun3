#define _GNU_SOURCE
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "native-bt-outcomes-435.h"
int main(void)
{
    bt435_reset();
    const unsigned char scan[]={1,0x42,0x20,6,1,0,0,0,0,0};
    assert(bt340_command(scan,sizeof(scan))==1);
    assert(bt340_command(scan,sizeof(scan)-1)==0);
    const unsigned events[]={3,5,6,8,0x36};
    const unsigned sizes[]={11,4,3,4,7};
    for(unsigned i=0;i<5;++i){
        unsigned char p[32];memset(p,0xa5,sizeof(p));
        p[0]=4;p[1]=events[i];p[2]=sizes[i];p[3]=0;
        assert(bt435_event(p,sizes[i]+3)==3);
        p[3]=5;assert(bt435_event(p,sizes[i]+3)==3);
        for(size_t n=0;n<sizes[i]+3;++n)assert(bt435_event(p,n)==0);
        p[2]--;assert(bt435_event(p,sizes[i]+2)==0);
    }
    unsigned char le[15]={4,0x3e,12,2,1};
    assert(bt435_event(le,sizeof(le))==2);
    assert(bt435.le_packets==1&&bt435.classic_packets==0&&bt435.outcomes==10);
    le[13]=1;assert(bt435_event(le,sizeof(le))==0);
    unsigned char classic[18]={4,2,15,1};
    assert(bt435_event(classic,sizeof(classic))==2);
    assert(bt435.classic_packets==1);
    unsigned char key[26]={4,0x18,23};
    memset(key+3,0xa5,23);assert(bt435_event(key,sizeof(key))==0);
    bt435_summary();
    bt435.le_packets=UINT64_MAX;bt435_increment(&bt435.le_packets);
    assert(bt435.le_packets==UINT64_MAX&&bt435.saturated==1);
    bt435_reset();assert(bt435.le_packets==0&&bt435.outcomes==0&&!bt435.saturated);
    bt435_summary();
    puts("BT436 outcome_lengths_truncation_privacy_counters_reset=pass physical_pairing=0");
}
