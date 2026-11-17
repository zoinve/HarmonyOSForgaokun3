"""One new boot only; network return alone is not an automatic-exit claim."""
from pathlib import Path
source=Path(__file__).with_name('run-commercial-native-001.py').read_text().replace('commercial61-native-001','commercial61-native-010')
source=source.replace("'matebook'","'-o','HostName=10.126.126.14','-o','HostKeyAlias=192.168.10.128','matebook'")
anchor='import subprocess;subprocess.run('
admission="import subprocess;from pathlib import Path;mem={l.split(':')[0]:int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemTotal:','MemAvailable:'))};assert mem['MemTotal']>=15*1024**3 and mem['MemAvailable']>=11*1024**3,mem;subprocess.run("
assert source.count(anchor)==1
source=source.replace(anchor,admission,1)
source=source.replace('returned=False,sdk_userland=False','returned=False,return_classification="ubuntu_online_only_pending_guest_exit_evidence",sdk_userland=False',1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
