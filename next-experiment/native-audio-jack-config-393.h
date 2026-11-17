/* Inspect only detector configuration and loader flags, never tokens or other env. */
static void audio393_config(long pid)
{
    char path[256],buffer[8192];int config=-1,environment=-1,secure=-1;
    snprintf(path,sizeof(path),"/proc/%ld/root/system/etc/init/audio_server.cfg",pid);
    FILE *file=fopen(path,"r");
    if(file){
        size_t size=fread(buffer,1,sizeof(buffer)-1,file);buffer[size]=0;
        if(!ferror(file))config=strstr(buffer,"/vendor/lib64/harmony-graphics/audio-jack376.so")!=NULL;
        fclose(file);
    }
    snprintf(path,sizeof(path),"/proc/%ld/environ",pid);file=fopen(path,"r");
    if(file){
        size_t size=fread(buffer,1,sizeof(buffer)-1,file);buffer[size]=0;
        if(!ferror(file)){
            environment=0;
            for(size_t offset=0;offset<size;){
                size_t length=strnlen(buffer+offset,size-offset);
                if(length==size-offset)break;
                if(!strcmp(buffer+offset,"LD_PRELOAD=/vendor/lib64/harmony-graphics/audio-jack376.so"))environment=1;
                offset+=length+1;
            }
        }
        fclose(file);
    }
    snprintf(path,sizeof(path),"/proc/%ld/auxv",pid);file=fopen(path,"r");
    if(file){
        uint64_t pair[2];unsigned count=0;
        while(count++<128&&fread(pair,sizeof(pair),1,file)==1){
            if(pair[0]==23){if(pair[1]<=1)secure=(int)pair[1];break;}
            if(!pair[0])break;
        }
        fclose(file);
    }
    dprintf(1,"AUDIO393_CONFIG pid=%ld config_has_adapter=%d preload_environment=%d at_secure=%d credentials_changed=0\n",
        pid,config,environment,secure);
}
