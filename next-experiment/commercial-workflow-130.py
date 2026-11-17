"""Bounded original-service backlight validation; preserve the desktop baseline."""
from pathlib import Path
import json
import re
import runpy
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
configure_local_transport=runpy.run_path(str(BASE/'commercial-workflow-124.py'))['configure_local_transport']
OPERATIONS=['install-commercial-native','run-commercial-native','retrieve-commercial-evidence','verify-commercial-return']

def source130(operation):
    assert operation in OPERATIONS
    source=(ROOT/'reports/commercial61-native-123'/(operation+'.generated.py')).read_text()
    source=source.replace('commercial61-native-123','commercial61-native-130').replace('commercial-return-audit-123','commercial-return-audit-130').replace('ordered_chain_equals_full_123','ordered_chain_equals_full_130')
    if operation=='install-commercial-native':
        overlay=json.loads((ROOT/'reports/commercial61-native-130/overlay-result.json').read_text())
        source,count=re.subn(r"^assert overlay_result\['chain'\]==.*$","assert overlay_result['chain']=="+repr(overlay['chain']),source,flags=re.M)
        assert count==1
        source,count=re.subn(r"^assert overlay_result\['shared_parent_overlay_sha256'\]==.*$","assert overlay_result['shared_parent_overlay_sha256']=="+repr(overlay['shared_parent_overlay_sha256']),source,flags=re.M)
        assert count==1
        start=source.index("'initrd /commercial61-native-001/initrd.img'")
        end=source.index(',options',start)
        source=source[:start]+','.join(repr('initrd /'+path) for path in overlay['chain'])+source[end:]
        source=source.replace('OOBE original-schema development seed 123','native panel backlight driver 130')
        anchor="text='\\n'.join(['title "
        assert source.count(anchor)==1
        check="estimated130=len(options[8:])+sum(len('initrd=\\\\'+p.replace('/','\\\\'))+1 for p in "+repr(overlay['chain'])+")+1\nassert estimated130<1800,estimated130\n"
        source=source.replace(anchor,check+anchor,1)
    elif operation=='retrieve-commercial-evidence':
        previous=json.loads((ROOT/'reports/commercial61-native-124/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor='if p.name not in ['
        assert source.count(anchor)==1
        source=source.replace(anchor,anchor+repr(previous)+', '+repr('commercial61-native-087-8a37e4cd-deb7-433f-bbb0-fdd51847fba0')+', ',1)
    return source

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in [*OPERATIONS,'retain-entries']
    report=ROOT/'reports/commercial61-native-130'
    assert all(json.loads((report/'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1]=='retain-entries':
        runpy.run_path(str(BASE/'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
    else:
        source=source130(sys.argv[1])
        assert source==(report/(sys.argv[1]+'.generated.py')).read_text()
        exec(compile(source,sys.argv[1],'exec'),{'__name__':'__main__','__file__':str(BASE/(sys.argv[1]+'-130.py'))})
