"""Connect the original wired detector to the actual Gaokun jack evdev device."""
from pathlib import Path
import copy
import json
import os
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
OLD=runpy.run_path(str(BASE/'build-audio-native-365.py'))
AUDIO=OLD['AUDIO'];ONCE=AUDIO['ONCE']
LIBRARY='/vendor/lib64/harmony-graphics/audio-jack376.so'

def config378():
    read=runpy.run_path(str(BASE/'build-radio-native-261.py'))['image_read']
    original=json.loads(read('p111-system.kr990-ext4-v1.img','/system/etc/init/audio_server.cfg'))
    updated=copy.deepcopy(original)
    services=[service for service in updated['services'] if service['name']=='audio_server']
    assert len(services)==1
    service=services[0]
    assert service['path']==['/system/bin/sa_main','/system/profile/audio_server.json']
    assert service['uid']=='audio' and 'input' in service['gid'] and service['caps']==['SYS_NICE']
    assert not any(env['name']=='LD_PRELOAD' for env in service.get('env',[]))
    service.setdefault('env',[]).append(dict(name='LD_PRELOAD',value=LIBRARY))
    restored=copy.deepcopy(updated)
    restored_service=next(service for service in restored['services'] if service['name']=='audio_server')
    restored_service['env'].pop()
    original_service=next(service for service in original['services'] if service['name']=='audio_server')
    if 'env' not in original_service:del restored_service['env']
    assert restored==original
    passwd=read('p111-system.kr990-ext4-v1.img','/system/etc/passwd').decode()
    assert next(line.split(':')[2:4] for line in passwd.splitlines() if line.startswith('audio:'))==['1041','1041']
    return json.dumps(updated,indent=2).encode()

def runtime378(source):
    source=AUDIO['runtime321'](source)
    placeholder=r'''    int jack378_library=open("/run/commercial-vendor004/upper/lib64/harmony-graphics/audio-jack376.so",
        O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0644);
    if(jack378_library<0||close(jack378_library))fail("audio378 adapter placeholder");
    int jack378_trace=open("/run/commercial-vendor004/upper/lib64/harmony-graphics/audio-jack376.trace",
        O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);
    if(jack378_trace<0||fchown(jack378_trace,1041,1041)||close(jack378_trace))fail("audio378 trace placeholder");
'''
    source=ONCE(source,'    commercial_vendor016();',placeholder+'    commercial_vendor016();')
    binding=r'''    const char *jack378_sources[]={"/audio376/audio-jack376.so","/audio376/audio_server.cfg"};
    const char *jack378_targets[]={"/vendor/lib64/harmony-graphics/audio-jack376.so","/system/etc/init/audio_server.cfg"};
    for(unsigned i=0;i<2;++i){
        struct stat node;
        if(lstat(jack378_targets[i],&node)||!S_ISREG(node.st_mode)||
           mount(jack378_sources[i],jack378_targets[i],NULL,MS_BIND,NULL)||
           mount(NULL,jack378_targets[i],NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))fail("audio378 readonly detector binding");
    }
    dprintf(1,"AUDIO378_DETECTOR original_service=1 original_credentials=1 real_evdev=1 input_injected=0\n");
'''
    anchor='    dprintf(1,'+chr(34)+'RADIO261_ORIGINAL_HDF'
    return ONCE(source,anchor,binding+anchor)

def outer378(source,old_digest,digest):
    source=OLD['outer365'](source,old_digest,digest).replace(
        '/commercial61-native-365/bootstrap-runtime087','/commercial61-native-378/bootstrap-runtime087')
    helper=(BASE/'native-audio-jack-observe-376.h').read_text()
    source=ONCE(source,'static void native_original(void)\n{',helper+'\nstatic void native_original(void)\n{')
    return ONCE(source,'                if(i==4||i==7)audio321_observe(child);',
        '                if(i==4||i==7){audio321_observe(child);audio376_observe(child);}')

def extra378(compile_program,stage,entries):
    OLD['extra365'](compile_program,stage,entries)
    source=stage/'audio-jack376.c';source.open('x').write((BASE/'native-audio-jack-376.c').read_text())
    library=stage/'audio-jack376.so'
    compiler=str(AUDIO['BUILD']/'window-bridge/toolchain/ohos-cc')
    subprocess.run([compiler,'-O2','-Wall','-Wextra','-Werror','-fvisibility=hidden','-shared','-fPIC',
        '-Wl,--no-undefined',str(source),'-ldl','-pthread','-o',str(library)],check=True)
    required=[]
    for line in subprocess.check_output(['readelf','--dyn-syms','--wide',str(library)],text=True).splitlines():
        parts=line.split()
        if len(parts)>=8 and parts[6]=='UND' and parts[4]=='GLOBAL':required.append(parts[7].split('@')[0])
    image=runpy.run_path(str(BASE/'build-radio-native-261.py'))['image_read'](
        'p111-system.kr990-ext4-v1.img','/system/lib/ld-musl-aarch64.so.1')
    assert image.startswith(b'\x7fELF')
    fd=os.memfd_create('original-libc-readonly',os.MFD_CLOEXEC)
    try:
        with os.fdopen(os.dup(fd),'wb') as stream:stream.write(image)
        symbols=subprocess.check_output(['readelf','--dyn-syms','--wide','/proc/self/fd/'+str(fd)],
            text=True,pass_fds=(fd,))
    finally:os.close(fd)
    defined=set()
    for line in symbols.splitlines():
        parts=line.split()
        if len(parts)>=8 and parts[6]!='UND':defined.add(parts[7].split('@')[0])
    assert not set(required)-defined,sorted(set(required)-defined)
    entries['native-target/audio376']=(0o40755,b'')
    entries['native-target/audio376/audio-jack376.so']=(0o100755,library.read_bytes())
    entries['native-target/audio376/audio_server.cfg']=(0o100644,config378())
    (stage/'audio-jack-abi.json').open('x').write(json.dumps(dict(
        required_original_libc_symbols=sorted(required),missing_symbols=[],
        service_path_uid_gid_caps_permissions_unchanged=True,input_injected=False,
        original_images_modified=False),indent=2)+'\n')

if __name__=='__main__':
    runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
        378,runtime378,outer378,AUDIO['RADIO']['vendor297'],extra378)
