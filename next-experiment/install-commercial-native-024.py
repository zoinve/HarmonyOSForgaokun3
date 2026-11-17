"""Fresh standard-Ubuntu deployment; no reuse of 023's audited S4 session."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-022.py')))['source']
source=source.replace('commercial61-native-022','commercial61-native-024').replace('Original SceneBoard resource mounts 022','Local EGL bridge binding 024')
source=source.replace("=='disabled'","=='enabled'").replace("=='inactive'","=='active'").replace('timer_disabled=True','timer_enabled=True')
source=source.replace('installation-192-resume.','installation.')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
