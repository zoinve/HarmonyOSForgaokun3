"""Retain the admitted 095 transport and preservation gates for candidate 099."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
configure_local_transport = runpy.run_path(str(BASE/'commercial-workflow-095.py'))['configure_local_transport']


def source099(name):
    source = (ROOT/'reports/commercial61-native-095'/(name+'.generated.py')).read_text()
    source = source.replace('commercial61-native-095', 'commercial61-native-099').replace(
        'commercial-return-audit-095', 'commercial-return-audit-099').replace(
        'ordered_chain_equals_full_095', 'ordered_chain_equals_full_099').replace(
        'retain-commercial-entries-095.py', 'retain-commercial-entries-099.py').replace(
        'Guarded normal window close 095', 'Reference service-first desktop startup 099')
    if name == 'install-commercial-native':
        assert all(json.loads((ROOT/'reports/commercial61-native-099/admission-test.json').read_text()).values())
        grandparent = json.loads((ROOT/'reports/commercial61-native-094/overlay-result.json').read_text())
        parent = json.loads((ROOT/'reports/commercial61-native-095/overlay-result.json').read_text())
        new_chain = parent['chain']+['commercial61-native-099/initrd.img']
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']=="+repr(grandparent['sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']=="+repr(parent['sha256']),
            "assert overlay_result['chain']=="+repr(grandparent['chain']+['commercial61-native-099/initrd.img']):
                "assert overlay_result['chain']=="+repr(new_chain),
            "'initrd /commercial61-native-092/early094.img','initrd /commercial61-native-099/initrd.img',options":
                "'initrd /commercial61-native-092/early094.img','initrd /commercial61-native-095/initrd.img','initrd /commercial61-native-099/initrd.img',options",
            "assert sha(esp/'commercial61-native-092/early094.img')=="+repr(grandparent['sha256']):
                "assert sha(esp/'commercial61-native-092/early094.img')=="+repr(grandparent['sha256'])+
                "\nassert sha(esp/'commercial61-native-095/initrd.img')=="+repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
    if name == 'retrieve-commercial-evidence':
        previous_run = json.loads((ROOT/'reports/commercial61-native-095/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, 'if p.name not in ['+repr(previous_run)+', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source099(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
