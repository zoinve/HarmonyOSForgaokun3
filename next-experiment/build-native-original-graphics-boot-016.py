"""Grow only the fresh RAM data filesystem to 3 GiB; original images stay read-only."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-015.py'))
inner='#include <sys/vfs.h>\n'+p['inner'];capture=p['capture']
anchor='    dprintf(1,"NATIVE_ORIGINAL_DATA ram_backed=1'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
    struct statfs fs;
    if(statfs("/data",&fs) || fs.f_bsize!=4096)fail("RAM ext4 block size");
    unsigned long long blocks=3221225472ULL/4096;
    int resize=open("/data",O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    if(resize<0 || ioctl(resize,_IOW('f',16,unsigned long long),&blocks) || close(resize))fail("RAM ext4 genuine online growth");
    if(statfs("/data",&fs) || (unsigned long long)fs.f_blocks*fs.f_bsize<2800000000ULL)fail("RAM ext4 enlarged capacity");
    dprintf(1,"NATIVE_RAM_DATA016 bytes=%llu available=%llu original_userdata_attached=0\n",
        (unsigned long long)fs.f_blocks*fs.f_bsize,(unsigned long long)fs.f_bavail*fs.f_bsize);
'''+anchor)
outer=p['outer'].replace('native-original-015-%s','native-original-016-%s')
anchor='    if(okay && native_loop(3,"/native-target/scratch-data.ext4",536870912ULL))okay=0;'
assert outer.count(anchor)==1
outer=outer.replace(anchor,r'''
    if(okay){
        int ram=open("/native-target/scratch-data.ext4",O_RDWR|O_CLOEXEC|O_NOFOLLOW);
        struct stat st;
        if(ram<0 || fstat(ram,&st) || !S_ISREG(st.st_mode) || st.st_size!=536870912ULL ||
           ftruncate(ram,3221225472ULL))okay=0;
        if(ram>=0)close(ram);
    }
    if(okay && native_loop(3,"/native-target/scratch-data.ext4",3221225472ULL))okay=0;
''')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+repr(p['p']['p']['p']['p']['wrapper'])+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-015','native-original-graphics-boot-016')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
