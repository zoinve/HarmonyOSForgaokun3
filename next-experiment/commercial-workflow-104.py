"""Inherit completed 101 transport and preservation gates for observation 104."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
configure_local_transport = runpy.run_path(str(BASE/'commercial-workflow-101.py'))['configure_local_transport']


def source104(name):
    source = (ROOT/'reports/commercial61-native-101'/(name+'.generated.py')).read_text()
    source = source.replace('commercial61-native-101', 'commercial61-native-104').replace(
        'commercial-return-audit-101', 'commercial-return-audit-104').replace(
        'ordered_chain_equals_full_101', 'ordered_chain_equals_full_104').replace(
        'Reference-scoped SoftBus BLE preload removal 101', 'Original DFX server wait observation 104')
    if name == 'install-commercial-native':
        assert all(json.loads((ROOT/'reports/commercial61-native-104/admission-test.json').read_text()).values())
        parent = json.loads((ROOT/'reports/commercial61-native-101/overlay-result.json').read_text())
        older = json.loads((ROOT/'reports/commercial61-native-099/overlay-result.json').read_text())
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']=="+repr(older['sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']=="+repr(parent['sha256']),
            "assert overlay_result['chain']=="+repr(older['chain']+['commercial61-native-104/initrd.img']):
                "assert overlay_result['chain']=="+repr(parent['chain']+['commercial61-native-104/initrd.img']),
            "'initrd /commercial61-native-099/initrd.img','initrd /commercial61-native-104/initrd.img',options":
                "'initrd /commercial61-native-099/initrd.img','initrd /commercial61-native-101/initrd.img','initrd /commercial61-native-104/initrd.img',options",
            "assert sha(esp/'commercial61-native-099/initrd.img')=="+repr(older['sha256']):
                "assert sha(esp/'commercial61-native-099/initrd.img')=="+repr(older['sha256'])+
                "\nassert sha(esp/'commercial61-native-101/initrd.img')=="+repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
    if name == 'retrieve-commercial-evidence':
        previous_run = json.loads((ROOT/'reports/commercial61-native-101/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, 'if p.name not in ['+repr(previous_run)+', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source104(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
