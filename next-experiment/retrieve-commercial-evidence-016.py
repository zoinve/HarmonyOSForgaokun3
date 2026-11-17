"""Unique 016 run, read-only original evidence, successful r2 report directory."""
from pathlib import Path
source=Path(__file__).with_name('retrieve-native-evidence-033.py').read_text()
source=source.replace('reports/native-original-graphics-boot-033','reports/commercial61-native-016-r2')
source=source.replace('harmony-return-audit-033','commercial-return-audit-016').replace('native-interactive-033-*','commercial61-native-016-*')
source=source.replace("'matebook'","'-o','HostName=10.126.126.14','-o','HostKeyAlias=192.168.10.128','matebook'")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
