/* Read real evdev frames alongside MMI, without grabbing or injecting input. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>

enum { MAX_SLOTS = 32 };
struct contacts {
    unsigned slots, selected, maximum, frames, dropped;
    int ids[MAX_SLOTS], stale;
};

static unsigned active(const struct contacts *state)
{
    unsigned count=0;
    for (unsigned i=0;i<state->slots;++i) count+=state->ids[i]>=0;
    return count;
}

/* Return1 for a complete valid frame, -1 when a kernel resync is required. */
static int event(struct contacts *state, unsigned type, unsigned code, int value)
{
    if (type==EV_SYN && code==SYN_DROPPED) {
        state->stale=1; ++state->dropped; return 0;
    }
    if (state->stale) return type==EV_SYN && code==SYN_REPORT ? -1 : 0;
    if (type==EV_ABS && code==ABS_MT_SLOT) {
        state->selected=value<0 ? MAX_SLOTS : (unsigned)value;
    } else if (type==EV_ABS && code==ABS_MT_TRACKING_ID && state->selected<state->slots) {
        state->ids[state->selected]=value;
    } else if (type==EV_SYN && code==SYN_REPORT) {
        unsigned count=active(state);
        if (count>state->maximum) state->maximum=count;
        ++state->frames; return 1;
    }
    return 0;
}

static int resync(int fd, struct contacts *state)
{
    int values[MAX_SLOTS+1]={ABS_MT_TRACKING_ID};
    struct input_absinfo selected;
    if (ioctl(fd,EVIOCGMTSLOTS((state->slots+1)*sizeof(int)),values)<0 ||
        ioctl(fd,EVIOCGABS(ABS_MT_SLOT),&selected)<0 || selected.value<0 ||
        (unsigned)selected.value>=state->slots) return -1;
    memcpy(state->ids,values+1,state->slots*sizeof(int));
    state->selected=(unsigned)selected.value; state->stale=0;
    return 0;
}

static int selftest(void)
{
    struct contacts state={.slots=10};
    for (unsigned i=0;i<MAX_SLOTS;++i) state.ids[i]=-1;
#define CHECK(condition) do { if (!(condition)) return __LINE__; } while (0)
    CHECK(active(&state)==0);
    event(&state,EV_ABS,ABS_MT_TRACKING_ID,10);
    event(&state,EV_ABS,ABS_MT_SLOT,1);
    event(&state,EV_ABS,ABS_MT_TRACKING_ID,11);
    CHECK(event(&state,EV_SYN,SYN_REPORT,0)==1 && active(&state)==2 && state.maximum==2);
    event(&state,EV_ABS,ABS_MT_TRACKING_ID,-1);
    CHECK(active(&state)==1);
    event(&state,EV_ABS,ABS_MT_SLOT,99);
    event(&state,EV_ABS,ABS_MT_TRACKING_ID,12);
    CHECK(active(&state)==1);
    event(&state,EV_SYN,SYN_DROPPED,0);
    event(&state,EV_ABS,ABS_MT_SLOT,0);
    event(&state,EV_ABS,ABS_MT_TRACKING_ID,-1);
    CHECK(event(&state,EV_SYN,SYN_REPORT,0)==-1 && state.frames==1 && state.dropped==1);
    CHECK(active(&state)==1 && state.maximum==2);
    puts("TOUCH303_SELFTEST parser_only=1 hardware_acceptance=0 passed=1");
    return 0;
}

static long long milliseconds(void)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC,&now)) return -1;
    return (long long)now.tv_sec*1000+now.tv_nsec/1000000;
}

int main(int argc, char **argv)
{
    if (argc==2 && !strcmp(argv[1],"--self-test")) return selftest();
    if (argc!=1 || getuid()!=0) return 77;
    int fd=-1; char path[64],name[256];
    for (unsigned i=0;i<64;++i) {
        snprintf(path,sizeof(path),"/dev/input/event%u",i);
        int candidate=open(path,O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
        if (candidate<0) continue;
        memset(name,0,sizeof(name));
        if (ioctl(candidate,EVIOCGNAME(sizeof(name)),name)>=0 &&
            !strcmp(name,"Himax Capacitive TouchScreen")) {fd=candidate;break;}
        close(candidate);
    }
    struct input_absinfo slots;
    struct contacts state={0};
    int result=1;
    if (fd<0 || ioctl(fd,EVIOCGABS(ABS_MT_SLOT),&slots)<0 || slots.minimum!=0 ||
        slots.maximum<1 || slots.maximum>=MAX_SLOTS) goto finish;
    state.slots=(unsigned)slots.maximum+1;
    if (resync(fd,&state)) goto finish;
    dprintf(1,"TOUCH303_BEGIN node=%s slots=%u read_only=1 grab=0 injection=0 coordinates_exported=0\n",path,state.slots);
    long long start=milliseconds();
    if (start<0) goto finish;
    result=0;
    for (;;) {
        long long now=milliseconds();
        if (now<start) {result=1;break;}
        if (now-start>=120000) break;
        struct pollfd ready={fd,POLLIN,0};
        int count=poll(&ready,1,1000);
        if (count<0 && errno==EINTR) continue;
        if (count<0 || (ready.revents&(POLLERR|POLLHUP|POLLNVAL))) {result=1;break;}
        if (!count) continue;
        struct input_event events[64];
        ssize_t bytes=read(fd,events,sizeof(events));
        if (bytes<0 && (errno==EAGAIN || errno==EINTR)) continue;
        if (bytes<=0 || bytes%(ssize_t)sizeof(events[0])) {result=1;break;}
        for (size_t i=0;i<(size_t)bytes/sizeof(events[0]);++i) {
            int frame=event(&state,events[i].type,events[i].code,events[i].value);
            if (frame<0 && resync(fd,&state)) {result=1;break;}
        }
        if (result) break;
    }
finish:
    dprintf(1,"TOUCH303_END result=%d frames=%u max_concurrent=%u dropped=%u physical_multicontact_observed=%d app_delivery_verified=0\n",
        result,state.frames,state.maximum,state.dropped,!result && state.maximum>=2);
    if (fd>=0) close(fd);
    return result;
}
