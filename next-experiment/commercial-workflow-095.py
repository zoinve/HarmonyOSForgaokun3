"""Distinct normal-window-close candidate with inherited privacy/preservation gates."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
previous = runpy.run_path(str(BASE/'commercial-workflow-094.py'))
configure_local_transport = previous['configure_local_transport']


def source095(name):
    source = previous['source094'](name).replace('commercial61-native-094', 'commercial61-native-095').replace(
        'commercial-return-audit-094', 'commercial-return-audit-095').replace(
        'ordered_chain_equals_full_094', 'ordered_chain_equals_full_095').replace(
        'retain-commercial-entries-094.py', 'retain-commercial-entries-095.py').replace(
        'Original init physical hardware inputs 094', 'Guarded normal window close 095')
    if name == 'install-commercial-native':
        assert all(json.loads((BASE.parent/'reports/commercial61-native-095/admission-test.json').read_text()).values())
        parent = json.loads((BASE.parent/'reports/commercial61-native-094/overlay-result.json').read_text())
        chain = parent['chain']+['commercial61-native-095/initrd.img']
        old_allocation = """cluster=os.statvfs(esp).f_frsize
assert cluster>=4096
assert (root/'initrd.img').stat().st_size<cluster
assert shutil.disk_usage(esp).free>=32*1024**2+2*cluster"""
        replacements = {
            "assert overlay_result['shared_parent_overlay_sha256']=="+repr(parent['shared_parent_overlay_sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']=="+repr(parent['sha256']),
            "assert overlay_result['chain']=="+repr(parent['chain']):
                "assert overlay_result['chain']=="+repr(chain),
            "dest=esp/'commercial61-native-092';entry=esp/'loader/entries/commercial61-native-095.conf'\nassert dest.is_dir() and not dest.is_symlink() and not (dest/'early094.img').exists() and not entry.exists()":
                "dest=esp/'commercial61-native-095';entry=esp/'loader/entries/commercial61-native-095.conf'\nassert not dest.exists() and not entry.exists()",
            old_allocation:
                "cluster=os.statvfs(esp).f_frsize\nassert cluster>=4096\nassert shutil.disk_usage(esp).free>=32*1024**2+((root/'initrd.img').stat().st_size//cluster+4)*cluster\ndest.mkdir()",
            "'initrd /commercial61-native-092/early094.img',options":
                "'initrd /commercial61-native-092/early094.img','initrd /commercial61-native-095/initrd.img',options",
            "assert sha(esp/'commercial61-native-092/initrd.img')=="+repr(parent['shared_parent_overlay_sha256']):
                "assert sha(esp/'commercial61-native-092/initrd.img')=="+repr(parent['shared_parent_overlay_sha256'])+
                "\nassert sha(esp/'commercial61-native-092/early094.img')=="+repr(parent['sha256']),
        }
        for anchor, value in replacements.items():
            assert source.count(anchor) == 1, anchor
            source = source.replace(anchor, value, 1)
        source = source.replace("dest/'early094.img'", "dest/'initrd.img'")
    if name == 'verify-commercial-return':
        anchor = "sha(esp/'commercial61-native-092/early094.img')"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "sha(esp/'commercial61-native-095/initrd.img')", 1)
    if name == 'retrieve-commercial-evidence':
        runs = [json.loads((BASE.parent/f'reports/commercial61-native-{n}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                for n in ('087', '088', '089', '090', '091', '092')]
        interrupted = json.loads((BASE.parent/'reports/commercial61-native-094/interrupted-run-audit.json').read_text())['run']
        anchor = 'if p.name not in '+repr(runs)
        assert source.count(anchor) == 1
        source = source.replace(anchor, 'if p.name not in '+repr(runs+[interrupted]), 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source095(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
