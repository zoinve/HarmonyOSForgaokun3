"""Read-only bounded GPU candidate contract and all nine artifact hashes."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-041.py').is_file(),'missing bounded GPU candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-041.py'))
assert p['inner']==p['p']['inner']
assert 'left033=420' in p['outer'] and 'elapsed033<240' in p['outer']
assert 'native-interactive-041-%s' in p['outer']
assert "root/'native-render-041'" in p['payload']
assert 'automatic_input_injection=True' not in p['payload']
check=runpy.run_path(str(base/'test-native-render-boot-034.py'))['check'].replace('native-original-graphics-boot-034','native-original-graphics-boot-041')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=check,text=True).returncode)
