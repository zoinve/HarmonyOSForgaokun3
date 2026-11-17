"""New run only, read-only noload source mount, hashes and final unmount."""
from pathlib import Path
source=Path(__file__).with_name('retrieve-commercial-evidence-001.py').read_text().replace('commercial61-native-001','commercial61-native-010').replace('commercial-return-audit-001','commercial-return-audit-010')
source=source.replace("if __name__=='__main__':exec(","source=source.replace(\"'matebook'\",\"'-o','HostName=10.126.126.14','-o','HostKeyAlias=192.168.10.128','matebook'\")\nif __name__=='__main__':exec(")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
