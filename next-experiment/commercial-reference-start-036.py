"""Reuse pinned HarmonyMac readiness/launch source; no fabricated service readiness."""
from pathlib import Path
import hashlib
REFERENCE=Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')
if not REFERENCE.exists():
    REFERENCE=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')

def desktop_start():
    original=(REFERENCE/'ports/tests/native-desktop-start.sh').read_text()
    start=original.index('n=0\n')
    stop=original.index('# Use the same bounded')
    launch=original[start:stop]
    command='/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard'
    assert launch.count(command)==1
    # Same original SA checks and IDs. Unlike the development reference, fail
    # closed if its bounded wait expires: do not launch against absent services.
    guard='''if ! /system/bin/aurora/samgr-service-probe 401 501 4606 4607; then
    echo REFERENCE036_SERVICES_UNAVAILABLE
    exit 1
fi
'''
    launch=launch.replace(command,guard+command.replace('/system/bin/aa','/usr/bin/aa'),1)
    # Omit reference's guide force-stop, unconditional READY and permission-
    # denied dump: none establishes genuine desktop content on this target.
    return '#!/system/bin/sh\n'+launch

def repair(original):
    anchor='# Reference: HarmonyMac ports/tests/native-desktop-start.sh, normal Ability Manager entry.'
    assert original.count(anchor)==1 and 'REFERENCE036_SERVICES_UNAVAILABLE' not in original
    prefix,_=original.split(anchor)
    return prefix+anchor+'\n'+desktop_start().split('\n',1)[1]

def provenance():
    files=['ports/tests/native-desktop-start.sh','ports/tests/samgr-service-probe.cpp','ports/tools/build-system-probes.sh']
    return {name:hashlib.sha256((REFERENCE/name).read_bytes()).hexdigest() for name in files}
