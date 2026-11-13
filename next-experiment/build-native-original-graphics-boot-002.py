"""Add passive early-init diagnostics only; preserve candidate 001 unchanged."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent
previous = runpy.run_path(str(base/'build-native-original-graphics-boot-001.py'))
inner, outer = previous['inner'], previous['outer']
diagnostics = r'''
static void diagnostic_file_002(unsigned sample, const char *path)
{
    char text[32768]; errno=0;
    ssize_t n=read_path(path,text,sizeof(text)); int error=errno;
    if(n>=0)for(ssize_t i=0;i<n;++i)if(!text[i])text[i]=' ';
    dprintf(1,"NATIVE_DIAG002_FILE sample=%u path=%s bytes=%zd errno=%d\n%s\n",
        sample,path,n,error,n>=0?text:"");
}
static void diagnostic_state_002(unsigned sample)
{
    const char *files[]={"/proc/1/mountinfo","/proc/1/status","/proc/1/wchan",
        "/proc/1/stack","/proc/1/cmdline","/proc/1/task/1/children",
        "/proc/self/mountinfo","/proc/net/unix","/proc/cmdline"};
    for(unsigned i=0;i<sizeof(files)/sizeof(files[0]);++i)diagnostic_file_002(sample,files[i]);
    const char *paths[]={"/","/data","/data/service","/data/service/el0/startup/init",
        "/system/etc/init.cfg","/vendor/etc/init.matebookego.cfg","/vendor/etc/fstab.matebookego",
        "/dev/block/loop3","/dev/socket","/dev/unix/socket","/proc/1/root/data"};
    for(unsigned i=0;i<sizeof(paths)/sizeof(paths[0]);++i){
        struct stat st={0};errno=0;int rc=stat(paths[i],&st),error=errno;
        dprintf(1,"NATIVE_DIAG002_STAT sample=%u path=%s rc=%d errno=%d mode=%o uid=%u gid=%u dev=%llu ino=%llu\n",
            sample,paths[i],rc,error,(unsigned)st.st_mode,st.st_uid,st.st_gid,
            (unsigned long long)st.st_dev,(unsigned long long)st.st_ino);
        DIR *dir=opendir(paths[i]);if(!dir)continue;struct dirent *e;unsigned count=0;
        while((e=readdir(dir)) && count++<96)
            dprintf(1,"NATIVE_DIAG002_ENTRY sample=%u path=%s name=%s\n",sample,paths[i],e->d_name);
        closedir(dir);
    }
}
'''
anchor='static void graphics_observer_047(void)'
assert inner.count(anchor)==1
inner=inner.replace(anchor,diagnostics+'\n'+anchor)
inner=inner.replace('pid <= 1','pid <= 0')
anchor='                if (!strstr(text, "render_service")'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'''                dprintf(1,"NATIVE_DIAG002_PROCESS sample=%u pid=%ld cmd=%s\\n",sample,pid,text);
'''+anchor)
inner=inner.replace('        DIR *processes = opendir("/proc");',
                    '        diagnostic_state_002(sample);\n        DIR *processes = opendir("/proc");')
host = r'''
static void native_diagnostics(pid_t child)
{
    DIR *dir=opendir("/proc");if(!dir)return;struct dirent *e;unsigned count=0;
    while((e=readdir(dir)) && count<512){
        char *end=NULL;long pid=strtol(e->d_name,&end,10);
        if(!*e->d_name || *end || pid<=0)continue;
        char path[128],text[4096];snprintf(path,sizeof(path),"/proc/%ld/status",pid);
        if(read_text(path,text,sizeof(text)))continue;
        dprintf(1,"NATIVE_DIAG002_HOST_PROCESS target=%d pid=%ld\n%s\n",child,pid,text);++count;
    }
    closedir(dir);
}
'''
outer=outer.replace('static void native_original(void)',host+'\nstatic void native_original(void)')
outer=outer.replace('    if(okay){\n        static char stack', '''    if(okay){
        /* Only the temporary diagnostic kernel: retain early init printk evidence. */
        int rate=open("/proc/sys/kernel/printk_devkmsg",O_WRONLY|O_CLOEXEC);
        if(rate>=0){ssize_t n=write(rate,"on\\n",3);dprintf(1,"NATIVE_DIAG002_PRINTK rc=%zd errno=%d\\n",n,errno);close(rate);}
        static char stack''')
outer=outer.replace('                snapshot();if(got==child)',
                    '                native_diagnostics(child);snapshot();if(got==child)')
outer=outer.replace('native-original-001-%s','native-original-002-%s')
payload=previous['payload']
offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-001','native-original-graphics-boot-002')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
