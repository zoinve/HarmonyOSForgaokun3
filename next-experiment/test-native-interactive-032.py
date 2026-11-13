from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-032.py'))
assert 'reboot(' not in p['outer'] and 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET' in p['outer']
assert 'native-cursor-032-r2' in p['payload']
assert 'fchown(cursor032,6696,1003)' in p['inner']
assert 'native_persistent_capture030();' in p['inner']
assert 'native_swipe_017();' not in p['inner'] and 'native_keyboard_027();' not in p['inner']
s=runpy.run_path(str(base/'test-native-interactive-031.py'))['s'].replace('native-original-graphics-boot-031','native-original-graphics-boot-032')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=s,text=True).returncode)
