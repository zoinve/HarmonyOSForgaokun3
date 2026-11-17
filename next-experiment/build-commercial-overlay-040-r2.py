from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-040.py')))['payload']
payload=payload.replace("work=root/'commercial61-native-040';local=base.parent/'reports/commercial61-native-040'","work=root/'commercial61-native-040-r2';local=base.parent/'reports/commercial61-native-040-r2'",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
