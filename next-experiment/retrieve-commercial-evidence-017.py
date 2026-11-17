"""Read-only unique 017 evidence; no original journal replay."""
from pathlib import Path
source=Path(__file__).with_name('retrieve-commercial-evidence-016.py').read_text()
source=source.replace('commercial61-native-016-r2','commercial61-native-017').replace('commercial61-native-016-*','commercial61-native-017-*').replace('commercial-return-audit-016','commercial-return-audit-017')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
