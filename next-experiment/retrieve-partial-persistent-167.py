"""Allow an absent probe log only before original-init handoff and identity probes."""
from pathlib import Path
import runpy
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
if __name__=='__main__':
    assert sys.argv[1:]==['--pre-handoff-fix-1']
    report=ROOT/'reports/commercial61-native-167'
    assert not (report/'runtime-evidence').exists()
    source=(report/'retrieve-commercial-evidence.generated.py').read_text()
    old=" diagnostic=(run/'snapshot075-commercial-desktop086.log').read_bytes()"
    assert source.count(old)==1
    new=""" diagnostic_path=run/'snapshot075-commercial-desktop086.log'
 if diagnostic_path.is_file():
  diagnostic=diagnostic_path.read_bytes()
 else:
  phases=list(run.glob('phase-*.log'))
  assert phases
  forbidden=[b'COMMERCIAL001_HANDOFF',b'HARDWARE091_GETDEVUDID',b'PRIVACY093_ORIGINAL_UDID_HASH']
  assert all(not any(marker in p.read_bytes() for marker in forbidden) for p in phases), 'original init or identity probe ran; retain the original UDID guard'
  diagnostic=b''
"""
    source=source.replace(old,new,1)
    compile(source,'retrieve-partial-persistent-167','exec')
    (report/'retrieve-partial-pre-handoff-fix-1.generated.py').open('x').write(source)
    runpy.run_path(str(BASE/'commercial-workflow-167.py'))['configure_local_transport']()
    exec(compile(source,'retrieve-partial-persistent-167','exec'),{'__name__':'__main__','__file__':str(BASE/'retrieve-partial-persistent-167.py')})
