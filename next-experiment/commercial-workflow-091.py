"""Original APIs, real hardware input gates, preserved inherited raw labels."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
previous = runpy.run_path(str(BASE/'commercial-workflow-090.py'))
configure_local_transport = previous['configure_local_transport']


def source091(name):
    source = previous['source090'](name).replace('commercial61-native-090', 'commercial61-native-091').replace(
        'commercial-return-audit-090', 'commercial-return-audit-091').replace(
        'ordered_chain_equals_full_090', 'ordered_chain_equals_full_091').replace(
        'retain-commercial-entries-090.py', 'retain-commercial-entries-091.py').replace(
        'Real network callback refresh 090', 'Original hardware identity input 091')
    if name == 'install-commercial-native':
        admission = json.loads((BASE.parent/'reports/commercial61-native-091/admission-test.json').read_text())
        assert all(admission.values())
        parent = json.loads((BASE.parent/'reports/commercial61-native-090/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        replacements = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-091/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-091/initrd.img']),
            "assert sha(esp/'commercial61-native-089/initrd.img')==" + repr(old):
                "assert sha(esp/'commercial61-native-089/initrd.img')==" + repr(old) +
                "\nassert sha(esp/'commercial61-native-090/initrd.img')==" + repr(parent['sha256']),
            "'initrd /commercial61-native-089/initrd.img','initrd /commercial61-native-091/initrd.img'":
                "'initrd /commercial61-native-089/initrd.img','initrd /commercial61-native-090/initrd.img','initrd /commercial61-native-091/initrd.img'",
        }
        for anchor, replacement in replacements.items():
            assert source.count(anchor) == 1, anchor
            source = source.replace(anchor, replacement, 1)
    if name == 'retrieve-commercial-evidence':
        runs = [json.loads((BASE.parent/f'reports/commercial61-native-{n}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                for n in ('087', '088', '089', '090')]
        anchor = 'if p.name not in ' + repr(runs[:3])
        assert source.count(anchor) == 1
        source = source.replace(anchor, 'if p.name not in ' + repr(runs), 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source091(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
