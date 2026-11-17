"""One bounded diagnostic, preserving automatic Ubuntu screen-off."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-022.py')))['source'].replace('commercial61-native-022','commercial61-native-023')
source=source.replace("state['screenoff_timer']=='disabled'","state['screenoff_timer']=='enabled' and state['screenoff_timer_active']=='active'")
anchor="screenoff_timer=subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],text=True,capture_output=True).stdout.strip()"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+",screenoff_timer_active=subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],text=True,capture_output=True).stdout.strip()",1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
