"""Exact overlay with hash-verified firmware additions and no removed members."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-078.py'))['source']
source = source.replace('commercial61-native-078', 'commercial61-native-079').replace('commercial61-native-077', 'commercial61-native-078')
start = source.index('assert set(patch) == ')
end = source.index('\nassert dict(before, **patch)', start)
source = source[:start] + '''expected079={'init','native-target/samgr_standard005.cfg','native-target/commercial-desktop077.sh'}
assert expected079 <= set(patch)
assert all(n in expected079 or n.startswith('lib/firmware/ath11k') or n in {'lib/firmware/regulatory.db','lib/firmware/regulatory.db.p7s'} for n in patch)
assert 'lib/firmware/ath11k/WCN6855/hw2.0/amss.bin' in patch
assert 'lib/firmware/ath11k/WCN6855/hw2.1' in patch''' + source[end:]
source = source.replace('ordered_chain_equals_full_078', 'ordered_chain_equals_full_079')
assert source.count('assert len(blob) < 2 * 1024 * 1024') == 1
source = source.replace('assert len(blob) < 2 * 1024 * 1024', 'assert len(blob) < 8 * 1024 * 1024')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
