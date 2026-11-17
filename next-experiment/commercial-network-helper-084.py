"""Extend proven namespace entry with fixed, read-only network observations."""
from pathlib import Path

SOURCE = Path(__file__).with_name('network-supplicant-083.c').read_text()
SOURCE = SOURCE.replace('NETWORK083', 'NETWORK084').replace('-c/network083/wpa.conf', '-c/network084/wpa.conf')
SOURCE = SOURCE.replace('#include <errno.h>', '#include <errno.h>\n#include <arpa/inet.h>\n#include <ifaddrs.h>\n#include <netinet/in.h>')
anchor = '"scan_results", "status", "log"'
assert SOURCE.count(anchor) == 1
SOURCE = SOURCE.replace(anchor, '"scan_results", "status", "log", "network"', 1)
NETWORK = r'''
static void network084_file(const char *path)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) {
        dprintf(1,"NETWORK084_FILE_MISSING path=%s errno=%d\n",path,errno);
        return;
    }
    struct stat st;
    if (fstat(fd,&st) || !S_ISREG(st.st_mode)) { close(fd); return; }
    dprintf(1,"NETWORK084_FILE_BEGIN path=%s\n",path);
    char text[4096];
    unsigned bytes=0;
    while(bytes<16384){
        ssize_t n=read(fd,text,sizeof(text));
        if(n<0 && errno==EINTR)continue;
        if(n<=0)break;
        if(write(1,text,(size_t)n)!=n)break;
        bytes+=(unsigned)n;
    }
    close(fd);
    dprintf(1,"\nNETWORK084_FILE_END path=%s bytes=%u complete_not_inferred=1\n",path,bytes);
}

static int network084_observe(void)
{
    struct ifaddrs *head=NULL;
    if(getifaddrs(&head))return 90;
    unsigned count=0;
    for(struct ifaddrs *it=head;it && count<64;it=it->ifa_next,++count){
        if(!it->ifa_addr || strcmp(it->ifa_name,"wlan0"))continue;
        int family=it->ifa_addr->sa_family;
        if(family!=AF_INET && family!=AF_INET6)continue;
        char address[INET6_ADDRSTRLEN],mask[INET6_ADDRSTRLEN];
        const void *src=family==AF_INET ? (void *)&((struct sockaddr_in *)it->ifa_addr)->sin_addr :
            (void *)&((struct sockaddr_in6 *)it->ifa_addr)->sin6_addr;
        if(!inet_ntop(family,src,address,sizeof(address)))continue;
        strcpy(mask,"unknown");
        if(it->ifa_netmask){
            const void *value=family==AF_INET ? (void *)&((struct sockaddr_in *)it->ifa_netmask)->sin_addr :
                (void *)&((struct sockaddr_in6 *)it->ifa_netmask)->sin6_addr;
            if(!inet_ntop(family,value,mask,sizeof(mask)))strcpy(mask,"unknown");
        }
        dprintf(1,"NETWORK084_ADDRESS interface=wlan0 family=%d value=%s netmask=%s flags=%u\n",
                family,address,mask,it->ifa_flags);
    }
    freeifaddrs(head);
    const char *paths[]={"/proc/net/route","/proc/net/ipv6_route","/sys/class/net/wlan0/carrier",
        "/sys/class/net/wlan0/operstate","/data/local/tmp/l410-wifi-compat-v2/netmanager-v4.status",
        "/data/local/tmp/l410-wifi-compat-v2/natural-control-v6.status",
        "/data/service/el1/public/dhcp/dhcp_cache.conf"};
    for(unsigned i=0;i<sizeof(paths)/sizeof(paths[0]);++i)network084_file(paths[i]);
    return 0;
}

'''
anchor = 'static int run_mode(const char *mode)\n{'
assert SOURCE.count(anchor) == 1
SOURCE = SOURCE.replace(anchor, NETWORK + anchor + '\n    if(!strcmp(mode,"network"))return network084_observe();', 1)
