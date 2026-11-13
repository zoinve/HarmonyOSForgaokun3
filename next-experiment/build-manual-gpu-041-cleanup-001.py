"""One-member overlay: proven 041 composer with the original manual 032 init."""
from pathlib import Path
import ast, runpy, subprocess
base = Path(__file__).resolve().parent
prior = runpy.run_path(str(base / 'build-native-return-overlay-033.py'))['payload']
helpers = '\n'.join(ast.get_source_segment(prior, node) for node in ast.parse(prior).body
                    if isinstance(node, ast.FunctionDef) and node.name in {'parse', 'member'})
common = r'''
from pathlib import Path
import gzip, hashlib, json
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'manual-gpu-041-boot-cleanup-001'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/manual-gpu-041-boot-cleanup-001')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
'''
verification = common + helpers + r'''
old=parse(root/'native-original-graphics-boot-032/initrd.img')
overlay=parse(work/'manual-gpu-overlay.img')
key='native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'
assert set(overlay)=={key} and 'init' not in overlay
assert sha(root/'native-original-graphics-boot-032/initrd.img')=='78049c130b3ab1dcd8f29d192b168bed3681d16a8aa9c298e6b548987e51f8ad'
assert hashlib.sha256(overlay[key][1]).hexdigest()=='355eb845579d191f447451a96e29ab96b49f8144dcf830cdbeb8f5cdfcf7404e'
combined=old|overlay
assert combined['init']==old['init']
source=(root/'native-original-graphics-boot-032/init.c').read_text()
assert 'reboot(' not in source and 'waitpid(child,&state,0)' in source
assert 'sleep(420)' not in source and 'elapsed033' not in source
assert {n for n in old if old[n]!=combined[n]}=={key}
manifest=json.loads((work/'result.json').read_text())
assert manifest['overlay_sha256']==sha(work/'manual-gpu-overlay.img')
print(json.dumps(dict(manual_init_byte_identical_to_032=True,automatic_exit=False,
  original_041_gpu_composer=True,only_changed_member=key,runtime_boot_tested=False)))
'''
payload = common + helpers + r'''
assert not work.exists() and not local.exists()
old=parse(root/'native-original-graphics-boot-032/initrd.img')
key='native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'
data=(root/'native-render-041/libdisplay_composer_vdi_impl.z.so').read_bytes()
assert hashlib.sha256(data).hexdigest()=='355eb845579d191f447451a96e29ab96b49f8144dcf830cdbeb8f5cdfcf7404e'
raw=member(key,old[key][0],data,1)+member('TRAILER!!!',0,b'',2)
work.mkdir(); local.mkdir()
dest=work/'manual-gpu-overlay.img'
with dest.open('xb') as f:f.write(gzip.compress(raw,mtime=0))
r=dict(overlay_sha256=sha(dest),bytes=dest.stat().st_size,base_candidate=32,
  composer_candidate=41,only_changed_member=[key],automatic_exit=False,
  manual_init_unchanged=True,original_images_unchanged=True,runtime_boot_tested=False)
for p in [work/'result.json',local/'result.json']:
 with p.open('x') as f:json.dump(r,f,indent=2)
print(json.dumps(r,indent=2))
'''
if __name__ == '__main__':
    r = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=120)
    r.check_returncode()
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=verification, text=True, timeout=120).returncode)
