"""Append the locally bound EGL provider as well as the normal diagnostic delta."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-023.py')))['payload']
payload=payload.replace('commercial61-native-023','commercial61-native-024').replace('ordered_chain_equals_full_023=True','ordered_chain_equals_full_024=True')
anchor="'native-target/desktop-order020.sh'}"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"'native-target/desktop-order020.sh','native-target/graphics016/system/lib64/libEGL_impl.so'}",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
