/* Inspect only the original Bluetooth service in the target PID namespace. */
static void radio294_observe(pid_t target)
{
    char path[160]; struct stat expected;
    snprintf(path,sizeof(path),"/proc/%d/ns/pid",target);
    if (stat(path,&expected)) return;
    DIR *directory=opendir("/proc"); if (!directory) return;
    struct dirent *entry;
    while ((entry=readdir(directory))) {
        char *end; long pid=strtol(entry->d_name,&end,10);
        if (*end || pid<=0) continue;
        struct stat ns,owner;
        snprintf(path,sizeof(path),"/proc/%ld",pid);
        if (stat(path,&owner) || owner.st_uid!=3021) continue;
        snprintf(path,sizeof(path),"/proc/%ld/ns/pid",pid);
        if (stat(path,&ns) || ns.st_dev!=expected.st_dev || ns.st_ino!=expected.st_ino) continue;
        snprintf(path,sizeof(path),"/proc/%ld/comm",pid);
        FILE *file=fopen(path,"r"); char line[1024];
        int host=file && fgets(line,sizeof(line),file) && !strcmp(line,"blue_host\n");
        if (file) fclose(file);
        if (!host) continue;
        snprintf(path,sizeof(path),"/proc/%ld/maps",pid);
        file=fopen(path,"r"); unsigned maps=0;
        if (file) {
            while (fgets(line,sizeof(line),file)) {
                if (strstr(line,"libbt_vendor.z.so")) {
                    char *name=strchr(line,'/');
                    if (name) dprintf(1,"RADIO294_VENDOR_MAP pid=%ld path=%s",pid,name);
                    ++maps;
                }
            }
            fclose(file);
        }
        dprintf(1,"RADIO294_HOST pid=%ld vendor_maps=%u\n",pid,maps);
        const char *nodes[]={"/radio261/vendor.trace","/native-bt-broker.sock","/vendor/lib64/libbt_vendor.z.so"};
        for (unsigned i=0;i<3;++i) {
            snprintf(path,sizeof(path),"/proc/%ld/root%s",pid,nodes[i]);
            struct stat node; int result=stat(path,&node),error=result?errno:0;
            dprintf(1,"RADIO294_NODE index=%u result=%d errno=%d uid=%u mode=%o bytes=%lld\n",
                i,result,error,result?0:(unsigned)node.st_uid,result?0:node.st_mode,
                result?0:(long long)node.st_size);
        }
    }
    closedir(directory);
}
