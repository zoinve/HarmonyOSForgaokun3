"""Observe real public transaction state and mode without private offsets or synthetic commands."""
from pathlib import Path
import runpy,subprocess
p=runpy.run_path(str(Path(__file__).with_name('build-commercial-native-041.py')))
inner=p['inner'].replace('libcommercial_rs_observer041.so','libcommercial_rs_observer042.so')
outer=p['outer'].replace('commercial61-native-041','commercial61-native-042').replace('COMMERCIAL041','COMMERCIAL042')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-041','commercial61-native-042').replace('commercial-rs-observer-041','commercial-rs-observer-042-r3').replace('libcommercial_rs_observer041.so','libcommercial_rs_observer042.so')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
