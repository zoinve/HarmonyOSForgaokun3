"""Append a small, reversible SceneBoard resource-path correction."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-021.py')))['source']
source=source.replace('commercial61-native-021','commercial61-native-022').replace('Reference aa arguments 021','Original SceneBoard resource mounts 022')
source=source.replace('HostName=10.126.126.14','HostName=192.168.10.128')
# Preserve the earlier connection-timeout evidence rather than overwriting it.
source=source.replace("report/'installation.stdout'","report/'installation-192-resume.stdout'").replace("report/'installation.stderr'","report/'installation-192-resume.stderr'")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
