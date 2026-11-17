"""Preserve hashes and distinguish real filter discovery, app execution and pixels."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('analyze-commercial-minimal-018.py')))['source']
source=source.replace('commercial61-native-018','commercial61-native-019').replace('COMMERCIAL018','COMMERCIAL019')
anchor="with (root/'runtime-analysis.json')"
assert source.count(anchor)==1
source=source.replace(anchor,"data['seccomp_filter_name_failures']=h.count('get filter name failed')\ndata['seccomp_application_failures']=h.count('Failed to set app seccomp filter')\ndata['seccomp_evidence']=[l for l in h.splitlines() if 'seccomp' in l.lower()][-100:]\n"+anchor,1)
source=source.replace("'captures','mali_context_failure','desktop_verified'","'captures','mali_context_failure','seccomp_filter_name_failures','seccomp_application_failures','desktop_verified'")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
