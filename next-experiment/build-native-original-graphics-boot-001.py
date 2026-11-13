"""Build an isolated native original-init trial; does not install, select or reboot."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent
inner = runpy.run_path(str(base/'prepare-baremetal-sdk-original-init-054.py'))['source']
outer = runpy.run_path(str(base/'prepare-baremetal-diagnostic-init-015.py'))['source']

start=inner.index('#ifndef SDK_DISK_SELECTION_035_H')
end=inner.index('static void guest_permissive_config_047',start)
inner=inner[:start]+r'''
#include <dirent.h>
static void readonly_image(const char *serial, unsigned long long sectors, const char *target)
{
    const char *name = !strcmp(serial,"sdk-system") ? "loop0" :
                       !strcmp(serial,"sdk-vendor") ? "loop1" :
                       !strcmp(serial,"sdk-sysprod") ? "loop2" : NULL;
    if (!name) fail("native image mapping");
    char path[64]; snprintf(path,sizeof(path),"/dev/%s",name);
    int fd=open(path,O_RDONLY|O_CLOEXEC), ro=0;
    unsigned long long bytes=0;
    if(fd<0 || ioctl(fd,BLKROGET,&ro) || ro!=1 || ioctl(fd,BLKGETSIZE64,&bytes) || bytes!=sectors*512)
        fail("native read-only image identity");
    close(fd); directory(target,0755);
    if(mount(path,target,"ext4",MS_RDONLY|MS_NODEV,"noload")) fail("native immutable image mount");
    dprintf(1,"NATIVE_ORIGINAL_IMAGE device=%s target=%s readonly=1 noload=1\n",name,target);
}
static void volatile_ext4_data_037(void)
{
    int fd=open("/dev/loop3",O_RDWR|O_CLOEXEC), ro=1;
    if(fd<0 || ioctl(fd,BLKROGET,&ro) || ro) fail("RAM ext4 loop writable");
    close(fd);
    if(mount("/dev/loop3","/data","ext4",MS_NOSUID|MS_NODEV|MS_NOATIME,"data=ordered"))
        fail("RAM ext4 data mount");
    dprintf(1,"NATIVE_ORIGINAL_DATA ram_backed=1 fresh_ext4=1 original_userdata_attached=0\n");
}

'''+inner[end:]
inner=inner.replace('harmony-mesa','lab-freedreno003').replace('physical_gpu=0','physical_gpu=1')
inner=inner.replace('sample < 24','sample < 12').replace('sample == 9 || sample == 21','sample == 9')
inner=inner.replace('ohos.boot.hardware=hmos.emulator','ohos.boot.hardware=matebookego')
inner=inner.replace('!strstr(buffer, "dummy-virt")','!strstr(buffer, "Matebook E Go")')
inner=inner.replace('only disk-isolated QEMU virt allowed','native MateBook E Go required')
inner=inner.replace('!option(buffer, "harmony.original_init_test=1")',
                    '!option(buffer, "harmony.original_init_test=1") || !option(buffer, "harmony.native_original=1")')
anchor='        if (!S_ISCHR(st.st_mode) && !S_ISBLK(st.st_mode)) continue;'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+'''
        /* Never copy physical block nodes into the original-service root. */
        if (S_ISBLK(st.st_mode) &&
            (strncmp(entry->d_name, "loop", 4) || strlen(entry->d_name)!=5 ||
             entry->d_name[4]<'0' || entry->d_name[4]>'3')) continue;
        if (!strcmp(entry->d_name,"mem") || !strcmp(entry->d_name,"kmem") ||
            !strcmp(entry->d_name,"port") || !strncmp(entry->d_name,"watchdog",8)) continue;
''')
start=inner.index('    int console = open("/dev/console"')
end=inner.index('    directory("/sys/fs/selinux"',start)
inner=inner[:start]+'''    /* Keep inherited evidence descriptors, not the physical console. */
    directory("/dev/block",0755);
    for(unsigned i=0;i<4;++i){
        char p[64];snprintf(p,sizeof(p),"/dev/block/loop%u",i);
        if(mknod(p,S_IFBLK|0600,makedev(7,i)))fail("native fstab device nodes");
    }
'''+inner[end:]
anchor='    const char *names[] = {\n        "libEGL_impl.so"'
assert inner.count(anchor)==1
# Preserve the original VDI/service loading locations; the private DRM RUNPATH
# remains nested. Native board files replace emulator-specific imports/fstab.
anchor='    dprintf(1, "GRAPHICS054_PROVIDER'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'''    const char *board_from[] = {"/board-init.cfg", "/board-fstab"};
    const char *board_to[] = {"/vendor/etc/init.matebookego.cfg", "/vendor/etc/fstab.matebookego"};
    for(unsigned i=0;i<2;++i){
        int fd=open(board_to[i],O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0644);
        if(fd<0 || close(fd) || mount(board_from[i],board_to[i],NULL,MS_BIND,NULL) ||
           mount(NULL,board_to[i],NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))fail("native board config bind");
    }
'''+anchor)
# Discard a virtual-only alias. All GBM backend files use their compiled native path.
inner=inner.replace(',\n        {"lab-softpipe-167", "lab-freedreno003"}','')
inner=inner.replace('ORIGINAL_INIT054_','NATIVE_ORIGINAL001_').replace('GRAPHICS054_','NATIVE_GRAPHICS001_')

native = r'''
#include <linux/loop.h>
#include <linux/fs.h>
#include <sched.h>
#include <sys/ioctl.h>
#include <sys/sysmacros.h>
#include <signal.h>

static int native_fds[4]={-1,-1,-1,-1};
static int native_child(void *unused)
{
    (void)unused;
    if(mount(NULL,"/",NULL,MS_REC|MS_PRIVATE,NULL) || chdir("/native-target") || chroot(".") || chdir("/"))
        _exit(90);
    char *const args[]={"/bootstrap",NULL};
    char *const env[]={"PATH=/system/bin:/vendor/bin","HOME=/",NULL};
    execve(args[0],args,env);_exit(91);
}
static int native_loop(unsigned i,const char *backing,unsigned long long expected)
{
    struct stat st;
    int input=open(backing,(i==3?O_RDWR:O_RDONLY)|O_NOFOLLOW|O_CLOEXEC);
    if(input<0 || fstat(input,&st) || !S_ISREG(st.st_mode) || (unsigned long long)st.st_size!=expected)return -1;
    char node[64];snprintf(node,sizeof(node),"/dev/loop%u",i);
    if(mknod(node,S_IFBLK|0600,makedev(7,i)) && errno!=EEXIST)return -1;
    int fd=open(node,O_RDWR|O_CLOEXEC);
    if(fd<0)return -1;
    struct loop_config cfg={0};cfg.fd=(unsigned)input;
    cfg.info.lo_flags=i==3?LO_FLAGS_AUTOCLEAR:LO_FLAGS_READ_ONLY|LO_FLAGS_AUTOCLEAR;
    if(ioctl(fd,LOOP_CONFIGURE,&cfg))return -1;
    close(input); native_fds[i]=fd;
    int ro=-1;unsigned long long bytes=0;
    if(ioctl(fd,BLKROGET,&ro) || ro!=(i==3?0:1) || ioctl(fd,BLKGETSIZE64,&bytes) || bytes!=expected)return -1;
    dprintf(1,"NATIVE_LOOP index=%u readonly=%d bytes=%llu ram_data=%d\n",i,ro,bytes,i==3);
    return 0;
}
static void native_original(void)
{
    char text[8192];
    if(!budget_ready(85) || read_text("/proc/cmdline",text,sizeof(text)) ||
       !strstr(text,"harmony.native_original=1") || !strstr(text,"enforcing=0")){
        dprintf(1,"NATIVE_ORIGINAL_REFUSED optin_or_budget\n");return;
    }
    if(read_text("/sys/firmware/devicetree/base/model",text,sizeof(text)) || !strstr(text,"Matebook E Go")){
        dprintf(1,"NATIVE_ORIGINAL_REFUSED wrong_board\n");return;
    }
    if(identify("/dev/nvme0n1p2",text,sizeof(text)) ||
       !strstr(text,"UUID=ecdd7931-ca18-4d14-82cd-ba3c62ff7365\n") ||
       !strstr(text,"PART_ENTRY_UUID=79f840db-aaeb-417a-96e2-70f82b763230\n") ||
       !strstr(text,"TYPE=ext4\n")){
        dprintf(1,"NATIVE_ORIGINAL_REFUSED ubuntu_identity\n");return;
    }
    if(mount("/dev/nvme0n1p2","/mnt/ubuntu","ext4",MS_RDONLY|MS_NODEV|MS_NOSUID|MS_NOEXEC, "noload")){
        dprintf(1,"NATIVE_ORIGINAL_REFUSED ubuntu_ro_mount errno=%d\n",errno);return;
    }
    const char *prefix="/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/original-disks/";
    const char *names[]={"system.img","vendor.img","sys_prod.img"};
    const unsigned long long sizes[]={3670016000ULL,104857600ULL,1048576000ULL};
    int okay=1;
    for(unsigned i=0;i<3;++i){
        char p[512];snprintf(p,sizeof(p),"%s%s",prefix,names[i]);
        if(native_loop(i,p,sizes[i])){okay=0;break;}
    }
    if(okay && native_loop(3,"/native-target/scratch-data.ext4",536870912ULL))okay=0;
    if(okay){
        static char stack[1024*1024] __attribute__((aligned(16)));
        pid_t child=clone(native_child,stack+sizeof(stack),CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD,NULL);
        dprintf(1,"NATIVE_ORIGINAL_START real_pid=%d original_pid_in_namespace=1 credentials_unmodified=1\n",child);
        if(child>0){
            for(unsigned i=0;i<14;++i){
                int state=0;pid_t got=waitpid(child,&state,WNOHANG);
                dprintf(1,"NATIVE_ORIGINAL_SAMPLE index=%u child=%d status=%d\n",i,got,state);
                snapshot();if(got==child)break;sleep(5);
            }
            (void)kill(child,SIGKILL);
            (void)waitpid(child,NULL,WNOHANG);
        }
    }else dprintf(1,"NATIVE_ORIGINAL_REFUSED loop_setup errno=%d\n",errno);
    for(unsigned i=0;i<4;++i)if(native_fds[i]>=0)close(native_fds[i]);
    dprintf(1,"NATIVE_ORIGINAL_END readiness_not_inferred=1 desktop_verified=0\n");snapshot();
}

'''
anchor='int main(void)'
assert outer.count(anchor)==1
outer=outer.replace(anchor,native+anchor)
start=outer.index('            char *identity_read[]')
end=outer.index('            char *bindings[]',start)
outer=outer[:start]+outer[end:]
start=outer.index('                char *mesa[]')
end=outer.index('\n            }',start)
outer=outer[:start]+'                native_original();'+outer[end:]
outer=outer.replace('native-diag-001-%s','native-original-001-%s')

payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+r'''
from pathlib import Path
import gzip,hashlib,json,stat,subprocess,shutil,os
project=Path('/mnt/d/lab/HarmonyOSForMatebookego');base=project/'next-experiment'
root=Path('/home/zoinve/harmony-virgl-883');work=root/'native-original-graphics-boot-001'
local=project/'reports/native-original-graphics-boot-001'
assert not work.exists() and not local.exists();work.mkdir();local.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=180)
 assert r.returncode==0,(args,r.stdout,r.stderr)
 return r.stdout
package=json.loads((root/'baremetal-identity-native-package-002/result.json').read_text())
parent=Path(package['archive']);assert sha(parent)==package['archive_sha256']
raw=gzip.decompress(parent.read_bytes());entries={};pos=0
while True:
 h=raw[pos:pos+110];assert h[:6]==b'070701'
 v=[int(h[6+i*8:14+i*8],16) for i in range(13)];size,ns=v[6],v[11]
 name=raw[pos+110:pos+109+ns].decode();start=(pos+110+ns+3)&~3
 if name=='TRAILER!!!':break
 assert name not in entries;entries[name]=(v[1],raw[start:start+size]);pos=(start+size+3)&~3
assert 'init' not in entries
original_entries=dict(entries)
def add(name,mode,data):
 assert name not in entries,name
 entries[name]=(mode,data)
def directory(name):
 if name in entries:assert stat.S_ISDIR(entries[name][0]);return
 if '/' in name:directory(name.rsplit('/',1)[0])
 add(name,stat.S_IFDIR|0o755,b'')
def file(name,p,mode=0o644):
 if '/' in name:directory(name.rsplit('/',1)[0])
 add(name,stat.S_IFREG|mode,p.read_bytes())
for name,source in [('init',outer),('bootstrap',inner)]:
 p=work/(name+'.c');p.write_text(source)
 args=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(p),'-I',str(base),'-o',str(work/name)]
 if name=='init':args.insert(-2,str(base/'baremetal-diagnostic-core.c'))
 run(args)
file('init',work/'init',0o755)
file('native-target/bootstrap',work/'bootstrap',0o755)
for name in ['proc','sys','dev','usr','vendor','sys_prod','data','run','tmp','config','storage','mnt']:
 directory('native-target/'+name)
directory('mnt/ubuntu')
bundle=root/'native-original-graphics-bundle-001'
manifest=json.loads((bundle/'result.json').read_text())
for row in manifest['files']:
 rel=row['target'].lstrip('/')
 p=bundle/'bundle'/rel;assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
 if rel.startswith('system/lib64/'):
  target='native-target/graphics-egl/'+rel.removeprefix('system/lib64/')
 else:
  assert rel.startswith('vendor/lib64/harmony-graphics/')
  target='native-target/graphics-provider/'+p.name
 file(target,p)
cfg=root/'baremetal-sdk-original-init-048/graphics-init.cfg'
file('native-target/graphics-init.cfg',cfg)
board=work/'board-init.cfg';board.write_text(json.dumps(dict(jobs=[]))+'\n')
file('native-target/board-init.cfg',board)
fstab=work/'board-fstab';fstab.write_text('\n'.join([
 '/dev/block/loop0 /usr ext4 ro,noload wait,required',
 '/dev/block/loop1 /vendor ext4 ro,noload wait,required',
 '/dev/block/loop2 /sys_prod ext4 ro,noload wait,required',
 '/dev/block/loop3 /data ext4 rw,nosuid,nodev,noatime,data=ordered wait,reservedsize=104857600','']))
file('native-target/board-fstab',fstab)
scratch=work/'scratch-data.ext4'
with scratch.open('xb') as f:f.truncate(536870912)
run(['mke2fs','-q','-F','-t','ext4','-O','^metadata_csum,^64bit','-E','lazy_itable_init=0,lazy_journal_init=0',str(scratch)])
file('native-target/scratch-data.ext4',scratch,0o600)
assert all(entries[n]==v for n,v in original_entries.items())
def member(name,mode,data,ino):
 nb=name.encode()+b'\0';v=[ino,mode,0,0,2 if stat.S_ISDIR(mode) else 1,0,len(data),0,0,0,0,len(nb),0]
 h=b'070701'+''.join(f'{i:08x}' for i in v).encode()+nb
 return h+b'\0'*((-len(h))%4)+data+b'\0'*((-len(data))%4)
archive=work/'initrd.img'
with archive.open('xb') as out:
 with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0,compresslevel=6) as gz:
  for i,(name,(mode,data)) in enumerate(sorted(entries.items()),1):gz.write(member(name,mode,data,i))
  gz.write(member('TRAILER!!!',0,b'',len(entries)+1))
for name in ['linux','sc8280xp-huawei-gaokun3.dtb']:
 src=root/'baremetal-identity-native-package-002'/name;shutil.copyfile(src,work/name)
assert sha(work/'linux')==package['kernel_sha256'] and sha(work/'sc8280xp-huawei-gaokun3.dtb')==package['dtb_sha256']
artifacts=[]
for name in ['initrd.img','linux','sc8280xp-huawei-gaokun3.dtb','init','bootstrap','init.c','bootstrap.c','board-init.cfg','board-fstab']:
 p=work/name;artifacts.append(dict(name=name,bytes=p.stat().st_size,sha256=sha(p)))
d=dict(artifacts=artifacts,parent_entries_preserved=len(original_entries),native_mesa_files=len(manifest['files']),
 target_hardware='matebookego',original_service_credentials_unmodified=True,original_images_readonly=True,
 volatile_ext4_data=True,outer_deadline_seconds=180,original_service_observation_seconds=70,
 native_boot_attempted=False,original_service_runtime_verified=False,desktop_verified=False)
for dest in [work,local]:
 with (dest/'result.json').open('x') as f:json.dump(d,f,indent=2)
for name in ['init.c','bootstrap.c','board-init.cfg','board-fstab']:shutil.copyfile(work/name,local/name)
print(json.dumps(d,indent=2))
'''

if __name__ == '__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600)
    raise SystemExit(r.returncode)
