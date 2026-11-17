"""Observe actual config policy under original samgr identity, then exec the unchanged daemon."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-004.py'))
helper=r'''
static void commercial_copy005(const char *src,const char *dst,mode_t mode)
{
    int in=open(src,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    int out=open(dst,O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,mode);
    if(in<0 || out<0)fail("commercial observer copy open");
    char b[8192];ssize_t n;
    while((n=read(in,b,sizeof(b)))>0)if(write(out,b,(size_t)n)!=n)fail("commercial observer copy write");
    if(n<0 || close(in) || close(out))fail("commercial observer copy close");
}
static void commercial_profile005(void)
{
    directory("/run/commercial-profile005",0750);
    if(chown("/run/commercial-profile005",5555,5555))fail("commercial original samgr log ownership");
    directory("/run/commercial-system005",0700);
    directory("/run/commercial-system005/upper",0755);
    directory("/run/commercial-system005/work",0700);
    directory("/run/commercial-system005/upper/bin",0755);
    directory("/run/commercial-system005/upper/etc",0755);
    directory("/run/commercial-system005/upper/etc/init",0755);
    commercial_copy005("/native-target/samgr-observe","/run/commercial-system005/upper/bin/commercial-samgr005",0755);
    commercial_copy005("/native-target/samgr_standard005.cfg","/run/commercial-system005/upper/etc/init/samgr_standard.cfg",0644);
    const char *options="lowerdir=/system,upperdir=/run/commercial-system005/upper,workdir=/run/commercial-system005/work";
    if(mount("overlay","/system","overlay",MS_RDONLY,options))fail("commercial original-context observer overlay");
    dprintf(1,"COMMERCIAL005_PROFILE_OBSERVER original_samgr_uid=5555 service_fields_unchanged=1 observe_then_exec=1\n");
}
'''
inner=p['inner'].replace('int main(void)',helper+'\nint main(void)',1)
anchor='    guest_permissive_config_047();';assert inner.count(anchor)==1
inner=inner.replace(anchor,'    commercial_profile005();\n'+anchor,1)
anchor='        if(logn>0)dprintf(commercial_diag_fd003,"COMMERCIAL002_RS_LOG sample=%u bytes=%zd\\n%s\\n",sample,logn,text);'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+r'''
        ssize_t profile=read_path("/run/commercial-profile005/profile.log",text,sizeof(text));
        if(profile>0)dprintf(commercial_diag_fd003,"COMMERCIAL005_PROFILE_LOG sample=%u bytes=%zd\n%s\n",sample,profile,text);
''',1)
outer=p['outer'].replace('commercial61-native-004-%s','commercial61-native-005-%s').replace('COMMERCIAL004','COMMERCIAL005')
payload=p['payload'];assert payload.count('inner='+repr(p['inner']))==payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-004','commercial61-native-005')
addition=r'''
probe=root/'commercial-profile-005';probe_result=json.loads((probe/'result.json').read_text())
assert sha(probe/'samgr-observe')==probe_result['sha256']
original=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
r=subprocess.run(['debugfs','-R','cat /system/etc/init/samgr_standard.cfg',str(original)],capture_output=True,check=True)
cfg=r.stdout;old=b'"/system/bin/samgr"';new=b'"/system/bin/commercial-samgr005"'
assert cfg.count(old)==1
updated=cfg.replace(old,new,1)
a=json.loads(cfg);b=json.loads(updated)
assert a['services'][0]['name']=='samgr' and b['services'][0]['path'][0]=='/system/bin/commercial-samgr005'
b['services'][0]['path'][0]='/system/bin/samgr';assert a==b
entries['native-target/samgr-observe']=(stat.S_IFREG|0o755,(probe/'samgr-observe').read_bytes())
entries['native-target/samgr_standard005.cfg']=(stat.S_IFREG|0o444,updated)
(local/'original-samgr_standard.cfg').open('xb').write(cfg)
(local/'observer-samgr_standard.cfg').open('xb').write(updated)
'''
anchor=' def member('
assert payload.count('def member(')==1
payload=payload.replace('def member(',addition+'\ndef member(',1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
