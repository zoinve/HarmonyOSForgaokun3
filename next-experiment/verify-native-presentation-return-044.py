"""Verify mount restoration and actual callbacks, not a fabricated desktop FPS."""
from pathlib import Path

source = Path(__file__).with_name('verify-native-presentation-return-043.py').read_text()
for old, new in [('native-original-graphics-boot-043', 'native-original-graphics-boot-044'),
                 ('native-original-graphics-043', 'native-original-graphics-044'),
                 ('native-interactive-043-', 'native-interactive-044-'),
                 ('native-presentation-043-installation.json', 'native-presentation-044-installation.json')]:
    assert old in source, old
    source = source.replace(old, new)
anchor = '    native_marker = False'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n    runtime_mnt_observed = False')
anchor = '        raw = path.read_bytes()'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + r'''
        mount = re.search(rb'NATIVE_MNT044_READY type=1021994 flags=(\d+) mode=755 uid=0 gid=0 slave=1 original_early_calls=23500,23520', raw)
        if mount:
            flags = int(mount[1])
            assert flags & 2 and not flags & 1
            runtime_mnt_observed = True
''')
source = source.replace('    assert native_marker and modes', '    assert runtime_mnt_observed and native_marker and modes')
anchor = "    old_trial = base/'reports/baremetal-native-trial-012-collected'"
assert source.count(anchor) == 1
source = source.replace(anchor, '''    previous043 = base/'reports/native-original-graphics-boot-043/runtime-evidence'
    old043 = json.loads((previous043/'retrieval-manifest.json').read_text())
    for name,row in old043['files'].items(): check_file(previous043/'raw'/name,row)
''' + anchor)
anchor = "    result.update(raw_log_sizes_and_hashes_verified=len(manifest['files']),"
assert source.count(anchor) == 1
source = source.replace(anchor, "    result.update(original_runtime_mnt_mount_observed=runtime_mnt_observed,prior043_raw_files_verified=len(old043['files']),\n                  raw_log_sizes_and_hashes_verified=len(manifest['files']),")
compile(source, 'independent-native044-return', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-native044-return', 'exec'))
