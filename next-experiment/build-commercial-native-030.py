"""Observe actual client/output pixels and capture freshness, not EGL guesses."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-029.py'))
inner=p['inner']
assert '#include <time.h>' not in inner
inner=inner.replace('#include <unistd.h>','#include <unistd.h>\n#include <time.h>',1)
anchor='ssize_t n=read(fd,pixels,sizeof(pixels));close(fd);if(n<=0)return;'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'''struct stat before030={},after030={};
    int before_ok030=fstat(fd,&before030);
    ssize_t n=read(fd,pixels,sizeof(pixels));int after_ok030=fstat(fd,&after030);close(fd);if(n<=0)return;
    struct timespec now030={};clock_gettime(CLOCK_MONOTONIC,&now030);
    dprintf(commercial_diag_fd003,"COMMERCIAL030_CAPTURE_META sample=%u mono_sec=%lld mono_nsec=%ld before_ok=%d after_ok=%d bytes=%zd before_size=%lld after_size=%lld before_mtime_sec=%lld before_mtime_nsec=%ld after_mtime_sec=%lld after_mtime_nsec=%ld\\n",
      sample,(long long)now030.tv_sec,now030.tv_nsec,before_ok030,after_ok030,n,
      (long long)before030.st_size,(long long)after030.st_size,
      (long long)before030.st_mtim.tv_sec,before030.st_mtim.tv_nsec,
      (long long)after030.st_mtim.tv_sec,after030.st_mtim.tv_nsec);''',1)
outer=p['outer'].replace('commercial61-native-029-%s','commercial61-native-030-%s').replace('COMMERCIAL029','COMMERCIAL030')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-029','commercial61-native-030')
# Retain the first failed compilation and its generated source/logs verbatim.
payload=payload.replace("work=root/'commercial61-native-030';", "work=root/'commercial61-native-030-r2';",1)
extra=r'''
evidence=json.loads((root/'commercial-composer-030/result.json').read_text())
assert evidence['diagnostic_only'] and not evidence['sdk_runtime_libraries_used'] and evidence['public_exports_unchanged']
key='native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so'
mode,old_composer=entries[key]
assert hashlib.sha256(old_composer).hexdigest()==evidence['previous_composer_sha256']
new_composer=(root/'commercial-composer-030/libdisplay_composer_vdi_impl.z.so').read_bytes()
assert hashlib.sha256(new_composer).hexdigest()==evidence['composer_sha256']
entries[key]=(mode,new_composer)
(local/'composer-evidence-provenance.json').open('x').write(json.dumps(evidence,indent=2))
'''
anchor='def member(name,mode,data,ino):'
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
