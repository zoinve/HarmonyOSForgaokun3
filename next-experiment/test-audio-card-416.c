/* UCM lifecycle fixture: no physical PCM or microphone access. */
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
typedef int snd_use_case_mgr_t;
static int manager, opened, closed, inactive, fail_enable, fail_disable;
static int open_ucm(snd_use_case_mgr_t **out,const char *name)
{assert(!strcmp(name,"hw:SC8280XPHUAWEIG"));*out=&manager;opened++;return 0;}
static int close_ucm(snd_use_case_mgr_t *mgr)
{assert(mgr==&manager);closed++;return 0;}
static int set_ucm(snd_use_case_mgr_t *mgr,const char *key,const char *value)
{
    assert(mgr==&manager);
    if(!strcmp(key,"_verb")&&!strcmp(value,"Inactive"))inactive++;
    if(!strcmp(key,"_enadev")&&fail_enable)return -EIO;
    if(!strcmp(key,"_disdev")&&fail_disable)return -EIO;
    return 0;
}
static struct {
    int (*snd_use_case_mgr_open)(snd_use_case_mgr_t **,const char *);
    int (*snd_use_case_mgr_close)(snd_use_case_mgr_t *);
    int (*snd_use_case_set)(snd_use_case_mgr_t *,const char *,const char *);
} alsa={open_ucm,close_ucm,set_ucm};
#include "native-audio-card-410.h"
int main(void)
{
    assert(!strcmp(pcm410(2),"hw:SC8280XPHUAWEIG,3"));
    assert(!strcmp(pcm410(3),"hw:SC8280XPHUAWEIG,2"));
    assert(acquire410(4)==-ENOTSUP);
    assert(!acquire410(0));assert(!acquire410(2));
    assert(opened==1&&leases410()==2);
    assert(acquire410(1)==-EBUSY&&acquire410(3)==-EBUSY);
    assert(!release410(2)&&!inactive&&!closed&&leases410()==1);
    fail_enable=1;
    assert(acquire410(2)==-EIO&&leases410()==1&&!inactive&&!closed);
    fail_enable=0;
    assert(!acquire410(2));
    assert(!release410(0)&&!inactive&&!closed);
    assert(!release410(2)&&inactive==1&&closed==1);
    assert(!acquire410(0));fail_enable=fail_disable=1;
    assert(acquire410(2)==-EIO&&card410.faulted&&leases410()==1);
    fail_enable=fail_disable=0;
    assert(acquire410(2)==-EIO);
    assert(!release410(0)&&!card410.faulted);
    assert(!acquire410(3));assert(!release410(3));
    assert(opened==3&&closed==3&&inactive==3);
    assert(release410(3)==-EINVAL);
    puts("AUDIO416 shared_card_lifecycle=pass hardware_acceptance=0");
    return 0;
}
