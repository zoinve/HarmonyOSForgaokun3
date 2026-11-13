"""Restore target boot umask only; keep diagnostic evidence private."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'build-native-original-graphics-boot-003.py'))
inner,outer=previous['inner'],previous['outer']
old='    close(rooted);'
assert outer.count(old)==1
outer=outer.replace(old,old+'\n    umask(022); /* Target boot default; outer diagnostic logger retains 077. */')
outer=outer.replace('native-original-003-%s','native-original-004-%s')
old='    pid_t observer = fork();'
new='''    const char *dac_paths[]={"/system","/vendor","/run/system-upper","/run/vendor-upper","/system/bin/sa_main","/system/lib/ld-musl-aarch64.so.1"};
    for(unsigned i=0;i<sizeof(dac_paths)/sizeof(dac_paths[0]);++i){
        struct stat st={0};int rc=stat(dac_paths[i],&st);
        dprintf(1,"NATIVE_DAC004 path=%s rc=%d mode=%o uid=%u gid=%u\\n",dac_paths[i],rc,
            (unsigned)st.st_mode,st.st_uid,st.st_gid);
    }
    pid_t observer = fork();'''
assert inner.count(old)==1
inner=inner.replace(old,new)
payload=previous['payload']
offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-003','native-original-graphics-boot-004')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
