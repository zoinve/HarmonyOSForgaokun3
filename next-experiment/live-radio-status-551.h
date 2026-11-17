/* Fixed numeric observations only; neither raw logs nor control commands. */
#include <limits.h>

#ifndef DIAG_RADIO_MAXIMUM_READ
#define DIAG_RADIO_MAXIMUM_READ (64U * 1024U * 1024U)
#endif

struct radio551 {
    long interface_result, supplicant_result, last_pong, last_errno;
    unsigned ping_count;
};

static int radio551_number(const char **cursor,long *value)
{
    if(**cursor<'0' || **cursor>'9')return 0;
    char *end=NULL;
    errno=0;
    long number=strtol(*cursor,&end,10);
    if(errno || end==*cursor || number<0 || number>INT_MAX)return 0;
    *value=number;
    *cursor=end;
    return 1;
}

static void radio551_line(const char *line,struct radio551 *result)
{
    const char *interface="SHARE501_INTERFACE_ADD result=";
    const char *supplicant="SHARE501_SUPPLICANT_START result=";
    const char *ping="SHARE501_PING pong=";
    long first,second;
    if(!strncmp(line,interface,strlen(interface))){
        line+=strlen(interface);
        if(radio551_number(&line,&first) && first<=255 &&
           !strcmp(line," real_netdev_required=1"))result->interface_result=first;
    } else if(!strncmp(line,supplicant,strlen(supplicant))){
        line+=strlen(supplicant);
        if(radio551_number(&line,&first) && first<=255 &&
           !strcmp(line," group_connected_not_inferred=1"))result->supplicant_result=first;
    } else if(!strncmp(line,ping,strlen(ping))){
        line+=strlen(ping);
        if(!radio551_number(&line,&first) || first>1 || strncmp(line," errno=",7))return;
        line+=7;
        if(!radio551_number(&line,&second) || second>4095 ||
           strcmp(line," transfer_verified=0") || (first && second))return;
        result->last_pong=first;
        result->last_errno=second;
        ++result->ping_count;
    }
}

static int radio551_status(void)
{
    struct stat metadata;
    int fd=log_open("native",&metadata);
    if(fd<0 || metadata.st_size<0){if(fd>=0)close(fd);return 74;}
    off_t limit=metadata.st_size;
    if(limit>(off_t)DIAG_RADIO_MAXIMUM_READ)limit=(off_t)DIAG_RADIO_MAXIMUM_READ;
    struct radio551 result={-1,-1,-1,-1,0};
    char block[4096],line[8192];
    size_t used=0;
    off_t offset=0;
    int discard=0;
    while(offset<limit){
        size_t request=(size_t)(limit-offset);
        if(request>sizeof(block))request=sizeof(block);
        ssize_t n=pread(fd,block,request,offset);
        if(n<0 && errno==EINTR)continue;
        if(n<0){close(fd);return 74;}
        if(!n)break;
        offset+=n;
        for(ssize_t i=0;i<n;++i){
            if(block[i]=='\n'){
                if(!discard){line[used]=0;radio551_line(line,&result);}
                discard=0;used=0;
            } else if(!discard){
                if(!block[i] || used>=sizeof(line)-1){discard=1;used=0;}
                else line[used++]=block[i];
            }
        }
    }
    close(fd);
    printf("{\042interface_add_result\042:%ld,\042supplicant_start_result\042:%ld,"
           "\042ping_observations\042:%u,\042last_pong\042:%ld,\042last_ping_errno\042:%ld,"
           "\042scanned_bytes\042:%lld,\042snapshot_bytes\042:%lld,\042complete_snapshot_read\042:%s,"
           "\042current_connection_not_proven\042:true,\042file_transfer_verified\042:false}\n",
           result.interface_result,result.supplicant_result,result.ping_count,result.last_pong,
           result.last_errno,(long long)offset,(long long)metadata.st_size,
           offset==metadata.st_size ? "true":"false");
    return 0;
}
