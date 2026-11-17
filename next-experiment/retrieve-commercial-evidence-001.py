"""Read-only retrieval for the unique commercial run, never replay original LAB."""
from pathlib import Path
source=Path(__file__).with_name('retrieve-native-evidence-033.py').read_text()
source=source.replace('reports/native-original-graphics-boot-033','reports/commercial61-native-001')
source=source.replace('harmony-return-audit-033','commercial-return-audit-001').replace('native-interactive-033-*','commercial61-native-001-*')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
