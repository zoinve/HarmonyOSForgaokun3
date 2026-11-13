"""Actual submitted pixels and early account logs, never synthetic desktop evidence."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
if __name__=='__main__':
    path=base/'build-native-original-graphics-boot-012.py'
    assert path.exists(),'missing real scanout capture candidate'
    p=runpy.run_path(str(path))
    assert 'AccountMgrService' in p['inner']
    assert 'NATIVE_PIXELS012_BEGIN' in p['inner']
    assert 'DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ' in p['capture']
    assert 'native_capture_012(state.buffers[slot])' in p['payload']
    old=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-012'),text=True,timeout=120).returncode)
