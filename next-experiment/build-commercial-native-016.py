"""Original commercial services with separately built MateBook hardware drivers.

Only builds an independent artifact; no device access, installation or reboot.
"""
from pathlib import Path,PurePosixPath
import runpy,subprocess,json
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-010.py'))
bundle=json.loads((base.parent/'reports/commercial-graphics-bundle-016/result.json').read_text())
assert bundle['sdk_system_libraries_used'] is False
inner=p['inner'];outer=p['outer'].replace('commercial61-native-010-%s','commercial61-native-016-%s').replace('COMMERCIAL010','COMMERCIAL016')
groups={'vendor':[],'system':[]}
def dirs(path):
    result=[];current=PurePosixPath(path)
    while str(current) not in ('.','/'):
        result.append(current.as_posix());current=current.parent
    return list(reversed(result))
for item in bundle['files']:
    target=item['target']
    for kind in groups:
        if target.startswith('/'+kind+'/'):
            relative=target[len(kind)+2:]
            upper='/run/commercial-'+('vendor004' if kind=='vendor' else 'system005')+'/upper'
            dest=upper+'/'+relative
            groups[kind].append((target,dest,item['mode']))
helpers=r'''
static void commercial_copy005(const char *,const char *,mode_t);
static void commercial_drm016(void)
{
    directory("/dev/dri",0755);
    DIR *d=opendir("/sys/class/drm");if(!d)fail("real DRM class inventory");
    struct dirent *entry;unsigned cards=0,renders=0;
    while((entry=readdir(d))){
        int card=!strncmp(entry->d_name,"card",4) && entry->d_name[4]>='0' && entry->d_name[4]<='9';
        int render=!strncmp(entry->d_name,"renderD",7) && entry->d_name[7]>='0' && entry->d_name[7]<='9';
        if(!card && !render)continue;
        const char *digits=entry->d_name+(card?4:7);if(strspn(digits,"0123456789")!=strlen(digits))continue;
        char sys[512],node[512],value[128];unsigned maj,min;
        snprintf(sys,sizeof(sys),"/sys/class/drm/%.255s/dev",entry->d_name);
        if(read_path(sys,value,sizeof(value))<=0 || sscanf(value,"%u:%u",&maj,&min)!=2)
            fail("real DRM device number");
        snprintf(node,sizeof(node),"/dev/dri/%.255s",entry->d_name);
        struct stat st;
        if(lstat(node,&st)){
            if(errno!=ENOENT || mknod(node,S_IFCHR|0660,makedev(maj,min)))fail("real DRM node");
        }else if(!S_ISCHR(st.st_mode) || st.st_rdev!=makedev(maj,min))fail("DRM node identity mismatch");
        if(chown(node,0,1003) || chmod(node,0660))fail("original graphics group real DRM access");
        cards+=(unsigned)card;renders+=(unsigned)render;
        dprintf(1,"COMMERCIAL016_DRM node=%s major=%u minor=%u genuine_sysfs=1\n",node,maj,min);
    }
    closedir(d);if(!cards || !renders)fail("required actual DRM devices");
}
'''
for kind,items in groups.items():
    helpers+='static void commercial_'+kind+'016(void)\n{\n'
    seen=set()
    for target,dest,mode in items:
        for parent in dirs(str(PurePosixPath(dest).parent)):
            if parent not in seen:
                helpers+='    directory('+json.dumps(parent)+',0755);\n';seen.add(parent)
        helpers+='    commercial_copy005('+json.dumps('/graphics016'+target)+','+json.dumps(dest)+','+str(mode)+');\n'
    helpers+='}\n'
helpers+=r'''
static void commercial_graphics016(void)
{
    const char *param="/sys_prod/etc/param/hw_defaults.para";
    if(mount("/graphics016/sys_prod/etc/param/hw_defaults.para",param,NULL,MS_BIND,NULL) ||
       mount(NULL,param,NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))fail("normal MateBook graphics API selection");
    int fd=open("/data/native-perf-023.trace",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0660);
    if(fd<0 || fchown(fd,1003,3036) || fchmod(fd,0660) || close(fd))fail("original graphics trace writers");
    fd=open("/data/native-scanout-013.ppm",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0644);
    if(fd<0 || fchown(fd,3036,3036) || fchmod(fd,0644) || close(fd))fail("actual composer scanout evidence");
    dprintf(1,"COMMERCIAL016_GRAPHICS original_service_credentials_unchanged=1 own_hardware_backends=1 sdk_payload=0 original_cursor_adapter=1\n");
}
static void commercial_capture016(unsigned sample)
{
    if(sample!=3 && sample!=9 && sample!=15)return;
    static unsigned char pixels[131072];static char hex[262144];
    int fd=open("/data/native-scanout-013.ppm",O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    if(fd<0)return;
    ssize_t n=read(fd,pixels,sizeof(pixels));close(fd);if(n<=0)return;
    const char digits[]="0123456789abcdef";
    for(ssize_t i=0;i<n;++i){hex[2*i]=digits[pixels[i]>>4];hex[2*i+1]=digits[pixels[i]&15];}
    dprintf(commercial_diag_fd003,"COMMERCIAL016_SCANOUT sample=%u bytes=%zd hex=",sample,n);
    if(write(commercial_diag_fd003,hex,(size_t)n*2)!=(ssize_t)((size_t)n*2))_exit(123);
    dprintf(commercial_diag_fd003,"\nCOMMERCIAL016_SCANOUT_END sample=%u\n",sample);
}
'''
# Capture needs the previously declared private descriptor; helper declarations
# are inserted immediately before board setup, which follows its declaration.
anchor='static void commercial_board004(void)'
assert inner.count(anchor)==1
inner=inner.replace(anchor,helpers+'\n'+anchor,1)
for kind in groups:
    anchor='    const char *options="lowerdir=/'+kind+',upperdir='
    assert inner.count(anchor)==1
    inner=inner.replace(anchor,'    commercial_'+kind+'016();\n'+anchor,1)
anchor='    commercial_board004();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'    commercial_drm016();\n'+anchor,1)
anchor='    guest_permissive_config_047();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+'\n    commercial_graphics016();',1)
anchor='for(unsigned sample=0;sample<48;++sample){'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+'\n        commercial_capture016(sample);\n        char perf016[32768];\n        if(read_path("/data/native-perf-023.trace",perf016,sizeof(perf016))>0)dprintf(commercial_diag_fd003,"COMMERCIAL016_PERF sample=%u %s\\n",sample,perf016);',1)
# Observer is defined earlier than its capture helper.
anchor='static void commercial_observer(void)'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'static void commercial_capture016(unsigned);\n'+anchor,1)
inner=inner.replace('original_libraries=1','original_system_services=1 own_board_drivers=1')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-010','commercial61-native-016')
# Preserve the first failed compilation and its exact generated source/logs.
# No 016 device operation has occurred; this is an independent build attempt.
payload=payload.replace("work=root/'commercial61-native-016';local=base.parent/'reports/commercial61-native-016'", "work=root/'commercial61-native-016-r2';local=base.parent/'reports/commercial61-native-016-r2'")
extra=r'''
hardware=root/'commercial-graphics-bundle-016'
hardware_manifest=json.loads((hardware/'result.json').read_text())
assert hardware_manifest['sdk_system_libraries_used'] is False
for item in hardware_manifest['files']:
 target=item['target'];assert target.startswith(('/system/','/vendor/','/sys_prod/'))
 data=(hardware/'tree'/target.lstrip('/')).read_bytes()
 assert hashlib.sha256(data).hexdigest()==item['sha256']
 key='native-target/graphics016'+target
 assert key not in entries
 entries[key]=(stat.S_IFREG|item['mode'],data)
(local/'graphics-bundle-manifest.json').open('x').write(json.dumps(hardware_manifest,indent=2))
'''
assert payload.count('def member(name,mode,data,ino):')==1
payload=payload.replace('def member(name,mode,data,ino):',extra+'\ndef member(name,mode,data,ino):',1)
payload=payload.replace('original_init_services_libraries=True','original_init_service_binaries=True, original_system_libraries_except_board_backends=True, own_board_graphics_payload=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
