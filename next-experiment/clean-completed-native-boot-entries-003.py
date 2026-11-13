"""Remove only completed018..021 entries; retain recently reused017,022 and evidence."""
from pathlib import Path
source=Path(__file__).with_name('clean-completed-native-boot-entries-001.py').read_text()
assert source.count('range(1,11)')==1
source=source.replace('range(1,11)','range(18,22)').replace('native-original-graphics-011+0-1.conf','native-original-graphics-022+0-1.conf').replace('completed-boot-entry-cleanup-001.json','completed-boot-entry-cleanup-003.json')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
