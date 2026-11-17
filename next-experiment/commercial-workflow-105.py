"""Retain completed 104 transport and preservation gates for capture order 105."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
configure_local_transport = runpy.run_path(str(BASE/'commercial-workflow-104.py'))['configure_local_transport']


def source105(name):
    source = (ROOT/'reports/commercial61-native-104'/(name+'.generated.py')).read_text()
    source = source.replace('commercial61-native-104', 'commercial61-native-105').replace(
        'commercial-return-audit-104', 'commercial-return-audit-105').replace(
        'ordered_chain_equals_full_104', 'ordered_chain_equals_full_105').replace(
        'Original DFX server wait observation 104', 'Original DFX before proc survey 105')
    if name == 'install-commercial-native':
        assert all(json.loads((ROOT/'reports/commercial61-native-105/admission-test.json').read_text()).values())
        parent = json.loads((ROOT/'reports/commercial61-native-104/overlay-result.json').read_text())
        older = json.loads((ROOT/'reports/commercial61-native-101/overlay-result.json').read_text())
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']=="+repr(older['sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']=="+repr(parent['sha256']),
            "assert overlay_result['chain']=="+repr(older['chain']+['commercial61-native-105/initrd.img']):
                "assert overlay_result['chain']=="+repr(parent['chain']+['commercial61-native-105/initrd.img']),
            "'initrd /commercial61-native-101/initrd.img','initrd /commercial61-native-105/initrd.img',options":
                "'initrd /commercial61-native-101/initrd.img','initrd /commercial61-native-104/initrd.img','initrd /commercial61-native-105/initrd.img',options",
            "assert sha(esp/'commercial61-native-101/initrd.img')=="+repr(older['sha256']):
                "assert sha(esp/'commercial61-native-101/initrd.img')=="+repr(older['sha256'])+
                "\nassert sha(esp/'commercial61-native-104/initrd.img')=="+repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
    if name == 'retrieve-commercial-evidence':
        previous_run = json.loads((ROOT/'reports/commercial61-native-104/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, 'if p.name not in ['+repr(previous_run)+', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source105(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
