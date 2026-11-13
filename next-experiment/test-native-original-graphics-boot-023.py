from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-023.py').exists(),'missing landscape/performance candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-023.py'))
assert 'CLONE_NEWNET' in p['outer'] and 'native-qca-broker-022' in p['outer']
assert 'native-perf-023.trace' in p['inner']
assert 'landscape_copy_023' in p['payload'] and 'GL_RENDERER' in p['payload']
payload=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-023')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
