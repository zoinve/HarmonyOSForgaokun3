"""Stage a fresh inert candidate; actual ARM64 binaries must refuse ordinary execution."""
from pathlib import Path

source = Path(__file__).with_name('stage-native-original-graphics-boot-001.py').read_text()
source = source.replace('native-original-graphics-boot-001', 'native-original-graphics-boot-043')
anchor = 'assert not root.exists()'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
assert subprocess.check_output(['uname','-r'],text=True).strip()=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text()
''')
anchor = '    assert not dest.exists()'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
    audit=json.loads(Path('reports/native-presentation-package-043-independent/result.json').read_text())
    assert audit['overlay_sha256']=='b2a0581f8869ca1d5fb6ee62bd1d0b1866c32832c73d811411f53a6f076fa3f7'
    assert audit['original_images_independent_hashes'] and audit['archive_metadata_preserved']
    assert audit['installed'] is False and audit['native_boot_attempted'] is False
''')
compile(source, 'stage-native-presentation-043', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'stage-native-presentation-043', 'exec'), {'__name__': '__main__', '__file__': __file__})
