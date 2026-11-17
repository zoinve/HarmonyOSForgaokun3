"""Preserve 159 intact; append a small loader overlay with explicit parent-chain checks."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-161'
previous = runpy.run_path(str(BASE / 'commercial-workflow-159.py'))
configure_local_transport = previous['configure_local_transport']
OPERATIONS = previous['OPERATIONS']


def source161(operation):
    source = (ROOT / 'reports/commercial61-native-159' / (operation + '.generated.py')).read_text()
    source = source.replace('commercial61-native-159','commercial61-native-161')
    source = source.replace('commercial-return-audit-159','commercial-return-audit-161')
    if operation == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-159/overlay-result.json').read_text())
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        transformed_chain = [name.replace('commercial61-native-159','commercial61-native-161') for name in parent['chain']]
        assert source.count(repr(transformed_chain)) == 2
        source = source.replace(repr(transformed_chain),repr(overlay['chain']))
        anchor = "'initrd /commercial61-native-161/initrd.img',options"
        assert source.count(anchor) == 1
        source = source.replace(anchor,"'initrd /commercial61-native-159/initrd.img','initrd /commercial61-native-161/initrd.img',options",1)
        old, new = parent['shared_parent_overlay_sha256'],parent['sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor,"assert overlay_result['shared_parent_overlay_sha256']==" + repr(new),1)
        anchor = "assert sha(esp/'commercial61-native-157/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor,"assert sha(esp/'commercial61-native-159/initrd.img')==" + repr(new),1)
        source = source.replace('ordered_chain_equals_full_159','ordered_chain_equals_full_161')
        source = source.replace('estimated159','estimated161')
        source = source.replace('native dynamic-address live diagnostic 159','native staged storage diagnostic 161')
        digest = json.loads((REPORT / 'result.json').read_text())['live161']['helper_sha256']
        anchor = "status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)"
        assert source.count(anchor) == 1
        check = "staged=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-helper-161/live-debug161')\nassert staged.is_file() and not staged.is_symlink() and staged.stat().st_uid==0 and (staged.stat().st_mode & 0o777)==0o500\nassert sha(staged)==" + repr(digest) + '\n'
        source = source.replace(anchor,check + anchor,1)
        assert 'harmony.live_debug159=1' in source and 'harmony.live_debug161=1' not in source
    elif operation == 'retrieve-commercial-evidence':
        run = json.loads((ROOT / 'reports/commercial61-native-159/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor,anchor + repr(run) + ', ',1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in [*OPERATIONS,'retain-entries']
    assert all(json.loads((REPORT / 'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
    else:
        operation = sys.argv[1]
        source = source161(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source,operation,'exec'),{'__name__':'__main__','__file__':str(BASE / (operation + '-161.py'))})
