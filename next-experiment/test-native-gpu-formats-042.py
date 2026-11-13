from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('test-native-gpu-composer-041.py')))['payload']
payload=payload.replace('native-gpu-composer-041-tests','native-gpu-formats-042-tests').replace('test-native-gpu-composer-041.cpp','test-native-gpu-formats-042.cpp')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
