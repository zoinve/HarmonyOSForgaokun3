from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-024.py').exists(),'missing cached transfer candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-024.py'))
old=runpy.run_path(str(base/'build-native-original-graphics-boot-023.py'))
assert p['inner']==old['inner'],'keep input, service configuration and observation unchanged'
assert 'cached_landscape_copy_024' in p['payload']
assert 'static std::vector<unsigned char> cache_in_024,cache_out_024' in p['payload']
assert 'DMA_BUF_SYNC_END' not in p['adaptation'],'do not change DMA ownership handling'
payload=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-024')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
