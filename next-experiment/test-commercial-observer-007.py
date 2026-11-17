"""Diagnostic delivery contract; not proof of target service health."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-007.py').exists(),'missing observable diagnostic candidate'
p=runpy.run_path(str(base/'build-commercial-native-007.py'))
s=(base/'commercial-profile-007.c').read_text()
assert s.index('COMMERCIAL007_ENTRY')<s.index('int fd=open("/run/commercial-profile005/profile.log"')
assert 'LOG_OPEN fd=%d errno=%d' in s and 'setvbuf(out,NULL,_IONBF,0)' in s
assert 'execv("/system/bin/samgr",argv)' in s
assert 'setuid(' not in s and 'setgid(' not in s
assert '/system/etc/init/samgr_standard.cfg' in p['inner'] and 'COMMERCIAL007_MERGED' in p['inner']
assert "root/'commercial-profile-007'" in p['payload']
assert 'commercial61-original-001' in p['outer'] and 'left033=420' in p['outer']
assert 'elapsed033<240' in p['outer']
print('PASS: pre-open entry/error diagnostics, merged-file inspection, unchanged original samgr exec and bounded return')
