"""Read-only preservation check; never repeats the completed boot."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'verify-commercial-return-001.py').read_text()
source=source.replace('commercial61-native-001','commercial61-native-010')
source=source.replace("['ssh','matebook'", "['ssh','-o','HostName=10.126.126.14','-o','HostKeyAlias=192.168.10.128','-o','ConnectTimeout=10','matebook'")
anchor="assert not subprocess.run(['findmnt'"
assert source.count(anchor)==1
source=source.replace(anchor,"assert subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='inactive'\n"+anchor)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
