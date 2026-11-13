"""Fresh read-only collector: one measured 81 MB HiLog, unchanged total cap."""
from pathlib import Path

source = Path(__file__).with_name('retrieve-native-presentation-043.py').read_text()
old = 'assert p.stat().st_size<=64*1024*1024'
assert source.count(old) == 1
source = source.replace(old, 'assert p.stat().st_size<=(128*1024*1024 if p.name=="interactive-hilog030.log" else 64*1024*1024)')
old = 'assert member.size <= 64*1024*1024'
assert source.count(old) == 1
source = source.replace(old, 'assert member.size <= file_limit(name)')
anchor = 'def validate_members(blob, manifest):'
assert source.count(anchor) == 1
source = source.replace(anchor, '''def file_limit(name):
    return 128*1024*1024 if name == 'interactive-hilog030.log' else 64*1024*1024


''' + anchor)
source = source.replace('/mnt/harmony-return-audit-043', '/mnt/harmony-return-audit-043-attempt-002')
compile(source, 'fresh-043-readonly-evidence-collector', 'exec')
scope = {'__name__': __name__, '__file__': __file__}
exec(compile(source, 'fresh-043-readonly-evidence-collector', 'exec'), scope)
REMOTE = scope['REMOTE']
file_limit = scope['file_limit']
validate_members = scope['validate_members']
