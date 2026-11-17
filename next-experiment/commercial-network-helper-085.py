"""Fixed original-curl probes and bounded original freeze-log observation."""
from pathlib import Path
import runpy

SOURCE = runpy.run_path(str(Path(__file__).with_name('commercial-network-helper-084.py')))['SOURCE']
SOURCE = SOURCE.replace('#include <errno.h>', '#include <errno.h>\n#include <dirent.h>')
anchor = '"log", "network"'
assert SOURCE.count(anchor) == 1
SOURCE = SOURCE.replace(anchor, '"log", "network", "http", "https", "freeze"', 1)
PROBE = r'''
static int network085_probe(const char *mode)
{
    const char *url = !strcmp(mode,"https") ?
        "https://connectivitycheck.platform.hicloud.com/generate_204" :
        "http://connectivitycheck.platform.hicloud.com/generate_204";
    char *args[] = {"/system/bin/curl", "--silent", "--show-error",
        "--noproxy", "*", "--connect-timeout", "2", "--max-time", "4",
        "--output", "/dev/null", "--write-out",
        "NETWORK085_CURL http_code=%{http_code} remote_ip=%{remote_ip} namelookup=%{time_namelookup} ssl_verify_result=%{ssl_verify_result}\n",
        (char *)url, NULL};
    dprintf(1,"NETWORK085_PROBE mode=%s original_curl=1 tls_bypass=0 success_not_inferred=1\n",mode);
    execv(args[0],args);
    dprintf(2,"NETWORK085_EXEC_FAILED mode=%s errno=%d\n",mode,errno);
    return 87;
}

static int network085_freeze(void)
{
    const char *path="/data/log/eventlog/freeze";
    int fd=open(path,O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
    if(fd<0){dprintf(1,"FREEZE085_DIRECTORY_MISSING errno=%d\n",errno);return 88;}
    DIR *dir=fdopendir(fd);
    if(!dir){close(fd);return 89;}
    unsigned count=0,files=0;
    struct dirent *entry;
    while(count++<256 && files<16 && (entry=readdir(dir))){
        if(strncmp(entry->d_name,"THREAD_BLOCK_",13) ||
           (!strstr(entry->d_name,"_stack") && !strstr(entry->d_name,"_binder")))continue;
        struct stat st;
        int item=openat(dirfd(dir),entry->d_name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
        if(item<0)continue;
        if(fstat(item,&st) || !S_ISREG(st.st_mode)){close(item);continue;}
        ++files;
        dprintf(1,"FREEZE085_FILE_BEGIN name=%s size=%lld\n",entry->d_name,(long long)st.st_size);
        char text[4096]; unsigned bytes=0;
        while(bytes<131072){
            ssize_t n=read(item,text,sizeof(text));
            if(n<0 && errno==EINTR)continue;
            if(n<=0)break;
            if(write(1,text,(size_t)n)!=n)break;
            bytes+=(unsigned)n;
        }
        close(item);
        dprintf(1,"\nFREEZE085_FILE_END bytes=%u complete_not_inferred=1\n",bytes);
    }
    closedir(dir);
    dprintf(1,"FREEZE085_SUMMARY entries=%u files=%u bounded=1\n",count,files);
    return 0;
}

'''
anchor = 'static int run_mode(const char *mode)\n{'
assert SOURCE.count(anchor) == 1
SOURCE = SOURCE.replace(anchor, PROBE + anchor + '\n    if(!strcmp(mode,"http") || !strcmp(mode,"https"))return network085_probe(mode);\n    if(!strcmp(mode,"freeze"))return network085_freeze();', 1)
