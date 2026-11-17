"""Prepare2.12 P2P, real-controller probe and numeric-only live diagnostics."""
from pathlib import Path
import hashlib
import json
import runpy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
PRIOR=runpy.run_path(str(BASE/'build-share-native-502.py'))

def once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new,1)

def outer555(source,old_digest,digest):
    source=PRIOR['outer502'](source,old_digest,digest)
    source=source.replace('/commercial61-native-502/bootstrap-runtime087','/commercial61-native-555/bootstrap-runtime087')
    old='(!strcmp(mode,"start") || !strcmp(mode,"share-start")) ? 15:5'
    source=once(source,old,'!strcmp(mode,"compat-probe") ? 20 : '+old)
    anchor='                if((i==4 || i==10) && started083)'
    source=once(source,anchor,
        '                if(i==5 && started083)(void)network083_command(child,"compat-probe");\n'+anchor)
    record=json.loads((ROOT/'reports/live-radio-reader-553/result.json').read_text())
    digest=record['sha256']
    assert len(digest)==64 and all(c in '0123456789abcdef' for c in digest)
    install=r'''    if(okay){
        native_live159_load();
        char *reader551[]={"/bin/busybox","sh","-c",
            "test -f /live-radio551-reader && test ! -L /live-radio551-reader && "
            "test \042$(/bin/busybox sha256sum /live-radio551-reader)\042 = \042DIGEST551  /live-radio551-reader\042 && "
            "test -d /live-debug157-root/bin && test ! -L /live-debug157-root/bin && "
            "test -f /live-debug157-root/bin/diag && test ! -L /live-debug157-root/bin/diag && "
            "test ! -e /live-debug157-root/bin/diag551 && test ! -L /live-debug157-root/bin/diag551 && "
            "/bin/busybox cp /live-radio551-reader /live-debug157-root/bin/diag551 && "
            "/bin/busybox chmod 0500 /live-debug157-root/bin/diag551 && "
            "test \042$(/bin/busybox sha256sum /live-debug157-root/bin/diag551)\042 = \042DIGEST551  /live-debug157-root/bin/diag551\042 && "
            "/bin/busybox mv /live-debug157-root/bin/diag551 /live-debug157-root/bin/diag",NULL};
        int reader551_status=probe("live-radio-reader-551",reader551,3);
        dprintf(1,"LIVE551_READER_INSTALL status=%d ram_only=1 original_authentication_unchanged=1\n",reader551_status);
    }'''.replace('DIGEST551',digest)
    return once(source,'    if(okay)native_live159_load();',install)

def extra555(compile_program,stage,entries):
    PRIOR['extra502'](compile_program,stage,entries)
    helper=runpy.run_path(str(BASE/'compat-network-helper-526.py'))['SOURCE']
    compile_program('network555',helper)
    entries['network086-control']=(0o100755,(stage/'network555').read_bytes())
    entries['native-target/compat525']=(0o40700,b'')
    record=json.loads((ROOT/'reports/share-supplicant-543/result.json').read_text())
    binary=Path(record['binary']).read_bytes()
    assert hashlib.sha256(binary).hexdigest()==record['sha256']
    entries['native-target/share501/wpa_supplicant']=(0o100755,binary)
    mode,config=entries['native-target/share501/p2p.conf']
    assert config.count(b'update_config=0\n')==1
    entries['native-target/share501/p2p.conf']=(mode,config.replace(b'update_config=0\n',b'',1))
    record=json.loads((ROOT/'reports/live-radio-reader-553/result.json').read_text())
    binary=Path(record['binary']).read_bytes()
    assert hashlib.sha256(binary).hexdigest()==record['sha256']
    entries['live-radio551-reader']=(0o100555,binary)

if __name__ == '__main__':
    original=PRIOR['PRIOR']
    while 'runtime401' not in original:original=original['PRIOR']
    runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
        555,original['runtime401'],outer555,
        original['OLD']['AUDIO']['RADIO']['vendor297'],extra555)
