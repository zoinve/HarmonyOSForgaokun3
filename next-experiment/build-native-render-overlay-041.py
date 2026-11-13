from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-native-render-overlay-035.py')))['payload']
payload=payload.replace('native-original-graphics-boot-035','native-original-graphics-boot-041').replace('fresh_unused_035_scratch_not_installed','fresh_unused_041_scratch_not_installed')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
