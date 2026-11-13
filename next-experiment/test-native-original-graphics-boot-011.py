"""Ensure storage compatibility is service-local and preserves original identities."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
if __name__=='__main__':
    path=base/'build-native-original-graphics-boot-011.py'
    assert path.exists(),'missing storage-local native candidate builder'
    p=runpy.run_path(str(path))
    assert 'storage_daemon-local.cfg' in p['inner']
    assert 'setenv("LD_PRELOAD","/system/lib64/libnative_local_storage_001.so",1)' in p['wrapper']
    assert 'execv("/system/bin/storage_daemon"' in p['wrapper']
    old=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-011'),text=True,timeout=120).returncode)
