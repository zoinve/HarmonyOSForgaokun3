/* Throwaway diagnostic: forward unchanged arguments and return actual results. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>

static void report(const char *name, void *real, int result) {
    int saved=errno; Dl_info info={0};
    if(real) dladdr(real,&info);
    fprintf(stderr,"GPU917_AA call=%s real=%p library=%s result=%d\n",name,real,
            info.dli_fname?info.dli_fname:"unknown",result);
    errno=saved;
}
__attribute__((constructor)) static void loaded(void) {
    int saved=errno;
    fprintf(stderr,"GPU917_TRACE_LOADED uid=%u gid=%u\n",getuid(),getgid());
    errno=saved;
}
int trace_connect(void *self) __asm__("_ZN4OHOS5AAFwk20AbilityManagerClient7ConnectEv");
int trace_connect(void *self) {
    typedef int (*fn)(void *);
    fn real=(fn)dlsym(RTLD_NEXT,"_ZN4OHOS5AAFwk20AbilityManagerClient7ConnectEv");
    int result=real?real(self):-1; report("Connect",(void *)real,result); return result;
}
int trace_start(void *self,const void *want,int user,int request)
    __asm__("_ZN4OHOS5AAFwk20AbilityManagerClient12StartAbilityERKNS0_4WantEii");
int trace_start(void *self,const void *want,int user,int request) {
    typedef int (*fn)(void *,const void *,int,int);
    fn real=(fn)dlsym(RTLD_NEXT,"_ZN4OHOS5AAFwk20AbilityManagerClient12StartAbilityERKNS0_4WantEii");
    int result=real?real(self,want,user,request):-1;
    report("StartAbility",(void *)real,result); return result;
}
int trace_stop(void *self,const void *bundle,bool clear,int user)
    __asm__("_ZN4OHOS5AAFwk20AbilityManagerClient11KillProcessERKNSt3__h12basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEEbi");
int trace_stop(void *self,const void *bundle,bool clear,int user) {
    typedef int (*fn)(void *,const void *,bool,int);
    fn real=(fn)dlsym(RTLD_NEXT,"_ZN4OHOS5AAFwk20AbilityManagerClient11KillProcessERKNSt3__h12basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEEbi");
    int result=real?real(self,bundle,clear,user):-1;
    report("KillProcess",(void *)real,result); return result;
}
