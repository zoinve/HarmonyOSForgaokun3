"""Unique bounded storage/return test, with original commercial services intact."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-002.py')))['source']
source=source.replace('commercial61-native-002','commercial61-native-010').replace('minimal startup 002','8 GiB data and bounded return 010').replace('AUTO RETURN 7 MIN','AUTO RETURN 210 SEC')
source=source.replace("['ssh','matebook',","['ssh','-o','HostName=10.126.126.14','-o','HostKeyAlias=192.168.10.128','matebook',")
anchor='assert not root.exists();root.mkdir()'
admission="""mem={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemTotal:','MemAvailable:'))}
assert mem['MemTotal']>=15*1024**3 and mem['MemAvailable']>=11*1024**3,('RAM admission refused',mem)
assert subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='inactive'
"""
assert source.count(anchor)==1
source=source.replace(anchor,admission+anchor,1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
