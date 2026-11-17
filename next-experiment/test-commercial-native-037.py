"""036 regression fix preserves working launch and reference namespace."""
from pathlib import Path
import runpy
b=Path(__file__).resolve().parent
old=runpy.run_path(str(b/'build-commercial-native-036.py'))
new=runpy.run_path(str(b/'build-commercial-native-037.py'))
assert new['inner']==old['inner']
assert "patched=runpy.run_path(str(base/'commercial-desktop-retry-032.py'))['repair'](patched)" in new['payload']
assert "patched=runpy.run_path(str(base/'commercial-reference-start-036.py'))['repair'](patched)" not in new['payload']
assert "commercial-reference-namespace-036.py" in new['payload']
assert 'elapsed033<90' in new['outer'] and 'left033=210' in new['outer']
compile(new['payload'],'<037>','exec')
for stem in ['install-commercial-native','run-commercial-native','retrieve-commercial-evidence','verify-commercial-return']:
 s=runpy.run_path(str(b/(stem+'-037.py')))['source'];compile(s,stem,'exec')
 assert 'StrictHostKeyChecking=yes' in s and 'BatchMode=yes' in s
 assert 'HostName=192.168.10.128' in s and 'HostKeyAlias=192.168.10.128' in s
 assert 'commercial61-native-036' not in s
 if stem!='retrieve-commercial-evidence':assert "=='enabled'" in s and "=='active'" in s
print('PASS: reference namespace retained, prior launch order restored, deadlines and host guards intact')
