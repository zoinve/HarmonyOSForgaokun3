#ifndef NATIVE_BT_OUTCOMES_435_H
#define NATIVE_BT_OUTCOMES_435_H
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "native-bt-discovery-340.h"
/* Payload sizes: Linux v6.12 include/net/bluetooth/hci.h, packed HCI events.
 * Never inspect/export addresses, link keys, passkeys or remote names. */
static struct {
    uint64_t classic_packets, le_packets, outcomes;
    int saturated;
} bt435;
static void bt435_increment(uint64_t *value)
{
    if(*value==UINT64_MAX)bt435.saturated=1;
    else ++*value;
}
static void bt435_reset(void)
{memset(&bt435,0,sizeof(bt435));}
static int bt435_event(const unsigned char *p,size_t n)
{
    int classification=bt340_event(p,n);
    if(classification==2){
        if(p[1]==0x3e)bt435_increment(&bt435.le_packets);
        else bt435_increment(&bt435.classic_packets);
    }
    if(n<3||p[0]!=4||n!=(size_t)p[2]+3)return 0;
    size_t payload=0;
    switch(p[1]){
    case 0x03:payload=11;break;
    case 0x05:payload=4;break;
    case 0x06:payload=3;break;
    case 0x08:payload=4;break;
    case 0x36:payload=7;break;
    default:return classification;
    }
    if(n!=payload+3)return classification;
    bt435_increment(&bt435.outcomes);
    dprintf(1,"BT435_OUTCOME event=%02x status=%u pairing_acceptance_not_inferred=1 identities_exported=0\n",p[1],p[3]);
    return 3;
}
static void bt435_summary(void)
{
    dprintf(1,"BT435_SESSION classic_report_packets=%llu le_report_packets=%llu outcome_events=%llu saturated=%d device_count_not_inferred=1 identities_exported=0\n",
        (unsigned long long)bt435.classic_packets,(unsigned long long)bt435.le_packets,
        (unsigned long long)bt435.outcomes,bt435.saturated);
}
#endif
