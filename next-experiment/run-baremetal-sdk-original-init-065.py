"""Original graph unchanged; give only HiLog query children a genuine cache index."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-064.py')))['payload']
payload = payload.replace('baremetal-sdk-original-init-qemu-064', 'baremetal-sdk-original-init-qemu-065')
payload = payload.replace('baremetal-sdk-original-init-064', 'baremetal-sdk-original-init-065')
payload = payload.replace('GRAPHICS064_', 'GRAPHICS065_').replace('ORIGINAL_INIT064_', 'ORIGINAL_INIT065_')
anchor = "add('graphics-init.cfg',stat.S_IFREG|0o444,Path(prep['files']['graphics-init.cfg']['path']).read_bytes())"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, anchor + '''
index_path=local.parent/'original-graphics-hilog-054/.dict_info.json'
assert sha(index_path)=='d8b36a8aca5c9adfd610395ba9de0368f782e475f7ae7d1be8241e8db8e5f50a'
index=json.loads(index_path.read_bytes())
assert index['ProductVersion'][0]['version']=='emulator 7.0.0.107(SP8DEVC00E47R1P3log)'
assert any(row['name']=='2CEB723E313C80C3605ECD369C0B8CB6' for row in index['uuid'])
add('graphics-dict-info.json',stat.S_IFREG|0o444,index_path.read_bytes())
''')
# Keep the parent's exclusive temporary-file naming disjoint as well.
payload = payload.replace('original-init-064-', 'original-init-065-')
compile(payload, 'original-graphics-065-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)
