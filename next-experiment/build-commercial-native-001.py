"""Commercial original-userland boot probe; no installer and no SDK payload."""
from pathlib import Path
import runpy,subprocess,sys
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-033.py'))
s=p['inner']
# Reuse generic Linux mount/capture helpers, NOT graphics, storage or SDK services.
inner=s[:s.index('static void diagnostic_file_002')]
inner=inner.replace('    reboot(RB_POWER_OFF);','    _exit(111);')
inner=inner.replace('"sdk-system"','"commercial-system"').replace('"sdk-vendor"','"commercial-vendor"').replace('"sdk-sysprod"','"commercial-sysprod"')
inner=inner.replace('!strcmp(serial,"commercial-sysprod") ? "loop2" : NULL;',
 '!strcmp(serial,"commercial-sysprod") ? "loop2" :\n                       !strcmp(serial,"commercial-chipprod") ? "loop4" : NULL;')
inner+=s[s.index('static void native_fault_walk_018'):s.index('static void native_keyboard_027')]
inner+='\n'+s[s.index('#ifndef NATIVE_CONTINUOUS_CAPTURE_030_H'):s.index('static void graphics_observer_047')]
main=s[s.index('int main(void)'):s.index('    dprintf(1, "NATIVE_ORIGINAL001_HANDOFF')]
main=main.replace('!option(buffer, "harmony.original_init_test=1")',
 '!option(buffer, "harmony.commercial=1") || !option(buffer, "harmony.original_init_test=1")')
main=main.replace("entry->d_name[4]>'3'","entry->d_name[4]>'4'").replace('i<4;++i','i<5;++i')
main=main.replace('readonly_image("sdk-system", 7168000, "/usr");','readonly_image("commercial-system", 16777216, "/usr");')
main=main.replace('readonly_image("sdk-vendor", 204800, "/vendor");','readonly_image("commercial-vendor", 2097152, "/vendor");')
main=main.replace('readonly_image("sdk-sysprod", 2048000, "/sys_prod");',
 'readonly_image("commercial-sysprod", 20000767, "/sys_prod");\n    readonly_image("commercial-chipprod", 2097152, "/chip_prod");')
inner+=r'''
static void commercial_observer(void)
{
    for(unsigned sample=0;sample<48;++sample){
        char path[128],text[16384];
        const char *files[]={"/sys/fs/selinux/enforce","/proc/1/status","/proc/1/wchan",
            "/proc/1/mountinfo","/system/etc/param/ohos.para","/data/service/el0/startup/init/param.para"};
        for(unsigned i=0;i<sizeof(files)/sizeof(files[0]);++i){
            ssize_t n=read_path(files[i],text,sizeof(text));
            if(n>=0)dprintf(1,"COMMERCIAL001_FILE sample=%u path=%s bytes=%zd\n%s\n",sample,files[i],n,text);
        }
        DIR *d=opendir("/proc");struct dirent *e;
        if(d){while((e=readdir(d))){
            char *end;long id=strtol(e->d_name,&end,10);if(!*e->d_name || *end || id<=0)continue;
            snprintf(path,sizeof(path),"/proc/%ld/cmdline",id);
            ssize_t n=read_path(path,text,sizeof(text));if(n<=0)continue;
            for(ssize_t i=0;i<n;++i)if(!text[i])text[i]=' ';
            dprintf(1,"COMMERCIAL001_PROCESS sample=%u pid=%ld cmd=%s\n",sample,id,text);
        }closedir(d);}
        sleep(5);
    }
    _exit(0);
}
'''+main+r'''
    /* Images are already mounted from verified immutable loop devices. Do not
       follow L410's physical PCIe/by-name paths on a different board. */
    if(mount("/commercial-mounts.cfg","/vendor/etc/fstab.l410-second-stage",NULL,MS_BIND,NULL) ||
       mount(NULL,"/vendor/etc/fstab.l410-second-stage",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))
        fail("commercial board mount configuration bind");
    const char *dirs[]={"/metadata","/storage","/log","/preload","/cust","/version","/patch_hw","/sec_storage","/config","/mnt"};
    for(unsigned i=0;i<sizeof(dirs)/sizeof(dirs[0]);++i)directory(dirs[i],0755);
    guest_permissive_config_047();
    native_persistent_capture030();
    pid_t observer=fork();if(observer<0)fail("commercial observer");
    if(!observer)commercial_observer();
    dprintf(1,"COMMERCIAL001_HANDOFF original_commercial_init=1 original_services=1 original_libraries=1 sdk_payload=0 readonly_images=4 volatile_data=1\n");
    char *const environment[]={"PATH=/system/bin:/vendor/bin","HOME=/",NULL};
    char *const arguments[]={"/system/bin/init", "--second-stage",NULL};
    execve(arguments[0], arguments, environment);
    fail("commercial original init exec");
}
'''
outer=p['outer'].replace('native-interactive-033-%s','commercial61-native-001-%s').replace('NATIVE_UNATTENDED033','COMMERCIAL001')
outer=outer.replace('native_fds[4]={-1,-1,-1,-1}','native_fds[5]={-1,-1,-1,-1,-1}')
outer=outer.replace('official-arm-sdk-921/original-disks/','commercial61-original-001/')
outer=outer.replace('"system.img","vendor.img","sys_prod.img"','"system.img","vendor.img","sysprod.img","chipprod.img"')
outer=outer.replace('3670016000ULL,104857600ULL,1048576000ULL','8589934592ULL,1073741824ULL,10240392704ULL,1073741824ULL')
outer=outer.replace('if(native_loop(i,p,sizes[i]))','if(native_loop(i==3?4:i,p,sizes[i]))')
outer=outer.replace('for(unsigned i=0;i<3;++i){\n        char p[512]','for(unsigned i=0;i<4;++i){\n        char p[512]')
outer=outer.replace('for(unsigned i=0;i<4;++i)if(native_fds[i]>=0)','for(unsigned i=0;i<5;++i)if(native_fds[i]>=0)')
start=outer.index('    char *qca_power[]');end=outer.index('    int ash=',start);outer=outer[:start]+outer[end:]
start=outer.index('        pid_t broker=fork();');end=outer.index('        static char stack[',start);outer=outer[:start]+outer[end:]
outer=outer.replace('        kill(broker,SIGKILL);waitpid(broker,NULL,0);','')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+r'''
from pathlib import Path
import gzip,hashlib,json,subprocess,stat,shutil,sys
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=root/'commercial61-native-001';local=base.parent/'reports/commercial61-native-001'
if work.exists():assert '--resume-compile' in sys.argv and not (work/'result.json').exists()
else:work.mkdir()
local.mkdir(exist_ok=True)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
archive=gzip.decompress((root/'native-original-graphics-boot-032/initrd.img').read_bytes())
entries={};offset=0
while True:
 h=archive[offset:offset+110];assert h[:6]==b'070701'
 v=[int(h[i:i+8],16) for i in range(6,110,8)];offset+=110
 name=archive[offset:offset+v[11]-1].decode();offset=(offset+v[11]+3)&~3
 data=archive[offset:offset+v[6]];offset=(offset+v[6]+3)&~3
 if name=='TRAILER!!!':break
 if name.startswith('native-target/') and not stat.S_ISDIR(v[1]) and name!='native-target/scratch-data.ext4':continue
 if 'native-qca-broker' in name:continue
 entries[name]=(v[1],data)
for name,source in [('init',outer),('bootstrap',inner)]:
 src=work/(name+'.c')
 if src.exists():assert src.read_text()==source
 else:src.write_text(source)
 cmd=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/(name+'.c')),'-I',str(base),'-o',str(work/name)]
 if name=='init':cmd.insert(-2,str(base/'baremetal-diagnostic-core.c'))
 attempt=0
 while (work/(name+'.stderr'+('.'+str(attempt) if attempt else ''))).exists():attempt+=1
 suffix='.'+str(attempt) if attempt else ''
 r=subprocess.run(cmd,capture_output=True);(work/(name+'.stdout'+suffix)).open('xb').write(r.stdout);(work/(name+'.stderr'+suffix)).open('xb').write(r.stderr)
 assert r.returncode==0,r.stderr.decode()
 entries['init' if name=='init' else 'native-target/bootstrap']=(stat.S_IFREG|0o755,(work/name).read_bytes())
entries['native-target/commercial-mounts.cfg']=(stat.S_IFREG|0o444,b'# Four commercial filesystems already mounted immutable by native bootstrap. No physical by-name mounts.\n')
assert not any(n.endswith('.so') or '/graphics-egl/' in n or '/graphics-provider/' in n for n,(m,d) in entries.items() if not stat.S_ISDIR(m))
def member(name,mode,data,ino):
 name=name.encode()+b'\0';v=[ino,mode,0,0,1,0,len(data),0,0,0,0,len(name),0]
 h=b'070701'+b''.join(f'{x:08x}'.encode() for x in v);out=h+name;out+=b'\0'*(-len(out)%4);out+=data;out+=b'\0'*(-len(out)%4);return out
raw=b''.join(member(n,m,d,i+1) for i,(n,(m,d)) in enumerate(entries.items()))+member('TRAILER!!!',0,b'',len(entries)+1)
image=work/'initrd.img';image.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
result=dict(artifacts=[dict(name=n,bytes=(work/n).stat().st_size,sha256=sha(work/n)) for n in ['init','bootstrap','init.c','bootstrap.c','initrd.img']],
 source_iso_sha256='25133f67c989084649b97a0ca577a640a28af27dbaf9a411ea7e87a4a795c0e2',sdk_payload=False,
 commercial_version_metadata='6.0.0.110 API 20',original_init_services_libraries=True,physical_installer_executed=False,
 original_userdata_attached=False,original_images_written=False,outer_deadline_seconds=420,target_budget_seconds=240,runtime_verified=False)
for n in ['result.json']:(work/n).write_text(json.dumps(result,indent=2));(local/n).open('x').write(json.dumps(result,indent=2))
for n in ['init.c','bootstrap.c','init.stdout','init.stderr','bootstrap.stdout','bootstrap.stderr']:shutil.copyfile(work/n,local/n)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-']+sys.argv[1:],input=payload,text=True,timeout=600).returncode)
