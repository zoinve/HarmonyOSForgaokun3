"""Remove exactly completed011..016 entries; keep current017 and all evidence."""
from pathlib import Path
source=Path(__file__).with_name('clean-completed-native-boot-entries-001.py').read_text()
assert source.count('range(1,11)')==1
source=source.replace('range(1,11)','range(11,17)').replace('native-original-graphics-011+0-1.conf','native-original-graphics-017+0-1.conf').replace('completed-boot-entry-cleanup-001.json','completed-boot-entry-cleanup-002.json')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
