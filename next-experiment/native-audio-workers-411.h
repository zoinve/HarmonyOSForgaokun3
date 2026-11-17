static pthread_mutex_t workers411_lock=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t workers411_done=PTHREAD_COND_INITIALIZER;
static struct worker411 {int fd,active;} workers411[2];
static void *worker411(void *argument)
{
    struct worker411 *worker=argument;
    client316(worker->fd);
    pthread_mutex_lock(&workers411_lock);
    close(worker->fd);worker->fd=-1;worker->active=0;
    pthread_cond_broadcast(&workers411_done);
    pthread_mutex_unlock(&workers411_lock);return NULL;
}
static int dispatch411(int client,pthread_attr_t *attributes)
{
    pthread_mutex_lock(&workers411_lock);
    int result=-EBUSY;
    for(unsigned i=0;i<2;++i)if(!workers411[i].active){
        workers411[i].fd=client;workers411[i].active=1;
        pthread_t thread;
        int error=pthread_create(&thread,attributes,worker411,&workers411[i]);
        if(error){workers411[i].active=0;workers411[i].fd=-1;result=-error;}
        else result=0;
        break;
    }
    pthread_mutex_unlock(&workers411_lock);return result;
}
int main(int argc,char **argv)
{
    if(argc!=2||getuid()!=0||strcmp(argv[1],"/native-target/native-audio315.sock"))return 77;
    signal(SIGPIPE,SIG_IGN);signal(SIGTERM,signal316);signal(SIGINT,signal316);
    if(load316())return 1;
    pthread_attr_t attributes;
    if(pthread_attr_init(&attributes)||pthread_attr_setdetachstate(&attributes,PTHREAD_CREATE_DETACHED))return 1;
    int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if(fd<0)return 1;
    struct sockaddr_un address={.sun_family=AF_UNIX};strcpy(address.sun_path,argv[1]);
    if(bind(fd,(struct sockaddr *)&address,sizeof(address))||chmod(argv[1],0600)||
       chown(argv[1],3127,3127)||listen(fd,2)){close(fd);return 1;}
    dprintf(1,"AUDIO411_LISTEN allowed_uid=3127 workers=2 real_capture_supported=1 samples_read=0\n");
    int status=0;
    while(!stopping){
        struct pollfd ready={fd,POLLIN,0};int available=poll(&ready,1,200);
        if(available<0&&errno==EINTR)continue;
        if(available<0||(ready.revents&(POLLERR|POLLHUP|POLLNVAL))){status=1;break;}
        if(!available)continue;
        int client=accept4(fd,NULL,NULL,SOCK_CLOEXEC);
        if(client<0){if(errno==EINTR)continue;status=1;break;}
        struct ucred peer;socklen_t size=sizeof(peer);
        struct timeval timeout={.tv_sec=3};
        if(getsockopt(client,SOL_SOCKET,SO_PEERCRED,&peer,&size)||peer.uid!=3127||
           setsockopt(client,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout))||
           setsockopt(client,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout))||dispatch411(client,&attributes))close(client);
    }
    stopping=1;close(fd);pthread_attr_destroy(&attributes);
    pthread_mutex_lock(&workers411_lock);
    for(unsigned i=0;i<2;++i)if(workers411[i].active)shutdown(workers411[i].fd,SHUT_RDWR);
    struct timespec deadline;clock_gettime(CLOCK_REALTIME,&deadline);deadline.tv_sec+=4;
    while(workers411[0].active||workers411[1].active){
        if(pthread_cond_timedwait(&workers411_done,&workers411_lock,&deadline)==ETIMEDOUT){status=1;break;}
    }
    unsigned active=(unsigned)workers411[0].active+(unsigned)workers411[1].active;
    dprintf(1,"AUDIO411_SHUTDOWN active_workers=%u status=%d\n",active,status);
    pthread_mutex_unlock(&workers411_lock);return status;
}
