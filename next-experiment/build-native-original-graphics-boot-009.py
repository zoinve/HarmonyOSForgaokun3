"""Correct passive log tags; no graphics or service behavior changes."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=runpy.run_path(str(base/'build-native-original-graphics-boot-008.py'))
inner=p['inner'].replace('COMPOSER_SRV,RSScreenManager,RSHardwareThread,HdiBackend,HdiDevice,RSMainThread','COMPOSER_SRV,Composer,RSScreenPreprocessor,RSScreenManager,RSHardwareThread,RSMainThread')
assert inner!=p['inner']
outer=p['outer'].replace('native-original-008-%s','native-original-009-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-008','native-original-graphics-boot-009')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
