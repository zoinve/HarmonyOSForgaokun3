"""Retain the one-boot and preservation gates with explicit parent 108 checks."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
configure_local_transport = runpy.run_path(str(BASE / 'commercial-workflow-108.py'))['configure_local_transport']


def source109(name):
    source = (ROOT / 'reports/commercial61-native-108' / (name + '.generated.py')).read_text()
    source = source.replace('commercial61-native-108', 'commercial61-native-109').replace(
        'commercial-return-audit-108', 'commercial-return-audit-109').replace(
        'ordered_chain_equals_full_108', 'ordered_chain_equals_full_109').replace(
        'Original memory wrapper directory prerequisites 108', 'Original memory service DFX and namespace 109')
    if name == 'install-commercial-native':
        assert all(json.loads((ROOT / 'reports/commercial61-native-109/admission-test.json').read_text()).values())
        parent = json.loads((ROOT / 'reports/commercial61-native-108/overlay-result.json').read_text())
        older = json.loads((ROOT / 'reports/commercial61-native-107/overlay-result.json').read_text())
        changes = {
            'assert overlay_result[\'shared_parent_overlay_sha256\']==' + repr(older['sha256']):
                'assert overlay_result[\'shared_parent_overlay_sha256\']==' + repr(parent['sha256']),
            'assert overlay_result[\'chain\']==' + repr(parent['chain'][:-1] + ['commercial61-native-109/initrd.img']):
                'assert overlay_result[\'chain\']==' + repr(parent['chain'] + ['commercial61-native-109/initrd.img']),
            "'initrd /commercial61-native-107/initrd.img','initrd /commercial61-native-109/initrd.img',options":
                "'initrd /commercial61-native-107/initrd.img','initrd /commercial61-native-108/initrd.img','initrd /commercial61-native-109/initrd.img',options",
            "assert sha(esp/'commercial61-native-107/initrd.img')==" + repr(older['sha256']):
                "assert sha(esp/'commercial61-native-107/initrd.img')==" + repr(older['sha256']) +
                "\nassert sha(esp/'commercial61-native-108/initrd.img')==" + repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
        # The outer runtime intentionally still loads byte-identical 108 runtime.
        runtime = json.loads((ROOT / 'reports/commercial61-native-109/result.json').read_text())['memstack109']
        assert runtime['runtime_path'].endswith('/commercial61-native-108/bootstrap-runtime087')
        anchor = "assert sha(root/'bootstrap-runtime087')==" + repr(runtime['runtime_sha256'])
        assert source.count(anchor) == 1
        remote_path = runtime['runtime_path'].removeprefix('/mnt/ubuntu')
        source = source.replace(anchor, anchor + '\nassert sha(Path(' + repr(remote_path) + '))==' + repr(runtime['runtime_sha256']), 1)
    if name == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-108/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
        'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source109(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
