#ifndef NATIVE_AUDIO_CARD_410_H
#define NATIVE_AUDIO_CARD_410_H
/* One card manager owns the shared verb; leases own only their exact device. */
static struct {
    pthread_mutex_t lock;
    snd_use_case_mgr_t *ucm;
    unsigned leases[4];
    int faulted;
} card410={.lock=PTHREAD_MUTEX_INITIALIZER};

static const char *device410(unsigned route)
{
    static const char *const names[]={"Speaker","Headphones","Mic","Headset"};
    return route<4?names[route]:NULL;
}
static const char *pcm410(unsigned route)
{
    static const char *const names[]={"hw:SC8280XPHUAWEIG,1","hw:SC8280XPHUAWEIG,0",
        "hw:SC8280XPHUAWEIG,3","hw:SC8280XPHUAWEIG,2"};
    return route<4?names[route]:NULL;
}
static unsigned leases410(void)
{return card410.leases[0]+card410.leases[1]+card410.leases[2]+card410.leases[3];}

static int finish410(void)
{
    if(leases410()||!card410.ucm)return 0;
    int result=alsa.snd_use_case_set(card410.ucm,"_verb","Inactive");
    int closed=alsa.snd_use_case_mgr_close(card410.ucm);
    card410.ucm=NULL;
    if(!result&&closed<0)result=closed;
    card410.faulted=result<0;
    return result;
}
static int acquire410(unsigned route)
{
    if(!device410(route))return -ENOTSUP;
    pthread_mutex_lock(&card410.lock);
    int result=0;
    unsigned direction=route<2?0:2;
    if(card410.faulted){result=-EIO;goto done;}
    if(card410.leases[direction]||card410.leases[direction+1]){result=-EBUSY;goto done;}
    if(!card410.ucm){
        result=alsa.snd_use_case_mgr_open(&card410.ucm,"hw:SC8280XPHUAWEIG");
        if(result<0)goto done;
        result=alsa.snd_use_case_set(card410.ucm,"_verb","HiFi");
        if(result<0){finish410();goto done;}
    }
    result=alsa.snd_use_case_set(card410.ucm,"_enadev",device410(route));
    if(result<0){
        int undone=alsa.snd_use_case_set(card410.ucm,"_disdev",device410(route));
        if(undone<0)card410.faulted=1;
        finish410();goto done;
    }
    card410.leases[route]=1;
    dprintf(1,"AUDIO410_LEASE route=%u action=acquire active=%u\n",route,leases410());
done:
    pthread_mutex_unlock(&card410.lock);return result;
}
static int release410(unsigned route)
{
    pthread_mutex_lock(&card410.lock);
    int result=0;
    if(route>=4||!card410.leases[route]||!card410.ucm){result=-EINVAL;goto done;}
    result=alsa.snd_use_case_set(card410.ucm,"_disdev",device410(route));
    card410.leases[route]=0;
    if(result<0)card410.faulted=1;
    int finished=finish410();
    if(!result&&finished<0)result=finished;
    dprintf(1,"AUDIO410_LEASE route=%u action=release active=%u result=%d\n",route,leases410(),result);
done:
    pthread_mutex_unlock(&card410.lock);return result;
}
#endif
