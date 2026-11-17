"""Original-init hardware input with allocation-aware reuse of an ESP directory."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
previous = runpy.run_path(str(BASE/'commercial-workflow-092.py'))
configure_local_transport = previous['configure_local_transport']
PAYLOAD = 'commercial61-native-092/early093.img'


def source093(name):
    source = previous['source092'](name).replace('commercial61-native-092', 'commercial61-native-093').replace(
        'commercial-return-audit-092', 'commercial-return-audit-093').replace(
        'ordered_chain_equals_full_092', 'ordered_chain_equals_full_093').replace(
        'retain-commercial-entries-092.py', 'retain-commercial-entries-093.py').replace(
        'Real early hardware model input 092', 'Original init physical hardware inputs 093')
    if name == 'install-commercial-native':
        assert all(json.loads((BASE.parent/'reports/commercial61-native-093/admission-test.json').read_text()).values())
        parent = json.loads((BASE.parent/'reports/commercial61-native-092/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        replacements = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-093/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + [PAYLOAD]),
            "assert sha(esp/'commercial61-native-091/initrd.img')==" + repr(old):
                "assert sha(esp/'commercial61-native-091/initrd.img')==" + repr(old) +
                "\nassert sha(esp/'commercial61-native-092/initrd.img')==" + repr(parent['sha256']),
            "'initrd /commercial61-native-091/initrd.img','initrd /commercial61-native-093/initrd.img'":
                "'initrd /commercial61-native-091/initrd.img','initrd /commercial61-native-092/initrd.img','initrd /" + PAYLOAD + "'",
            "options=options.replace('rdinit=/init ', 'rdinit=/early-hardware092.sh ', 1)":
                "options=options.replace('rdinit=/init ', 'rdinit=/early-hardware093.sh ', 1)",
            "dest=esp/'commercial61-native-093';entry=esp/'loader/entries/commercial61-native-093.conf'\nassert not dest.exists() and not entry.exists()":
                "dest=esp/'commercial61-native-092';entry=esp/'loader/entries/commercial61-native-093.conf'\nassert dest.is_dir() and not dest.is_symlink() and not (dest/'early093.img').exists() and not entry.exists()",
            'dest.mkdir()':
                "cluster=os.statvfs(esp).f_frsize\nassert cluster>=4096\nassert (root/'initrd.img').stat().st_size<cluster\nassert shutil.disk_usage(esp).free>=32*1024**2+2*cluster",
            "os.sync()\nassert all(sha(esp/n)==h for n,h in before.items())":
                "os.sync()\nassert entry.stat().st_size<cluster\nassert shutil.disk_usage(esp).free>=32*1024**2\nassert all(sha(esp/n)==h for n,h in before.items())",
        }
        for anchor, replacement in replacements.items():
            assert source.count(anchor) == 1, anchor
            source = source.replace(anchor, replacement, 1)
        source = source.replace("dest/'initrd.img'", "dest/'early093.img'")
    if name == 'verify-commercial-return':
        anchor = "assert sha(esp/'commercial61-native-093/initrd.img')"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert sha(esp/" + repr(PAYLOAD) + ")", 1)
    if name == 'retrieve-commercial-evidence':
        runs = [json.loads((BASE.parent/f'reports/commercial61-native-{n}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                for n in ('087', '088', '089', '090', '091', '092')]
        anchor = 'if p.name not in ' + repr(runs[:5])
        assert source.count(anchor) == 1
        source = source.replace(anchor, 'if p.name not in ' + repr(runs), 1)
        anchor = " needles=set(value for serial in serials for value in (serial,serial.lower(),serial.upper()))"
        guard = '''
 import re
 diagnostic=(run/'snapshot075-commercial-desktop086.log').read_bytes()
 identities=set(re.findall(rb'PRIVACY093_ORIGINAL_UDID_HASH digest=([0-9a-f]{64})', diagnostic))
 if re.search(rb'HARDWARE091_GETDEVUDID phase=before[^\\n]*valid_hex64=1', diagnostic):
  assert identities, 'original identity valid but privacy digest unavailable; refusing export'
 identity_pattern=re.compile(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])')
'''
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor+guard, 1)
        anchor = "    assert not any(value in data for value in needles),('physical serial found; refusing export',p.name)\n    tail=data[-15:]"
        replacement = """    assert not any(value in data for value in needles),('physical serial found; refusing export',p.name)
    assert not any(hashlib.sha256(match.group().upper()+b'\\n').hexdigest().encode() in identities for match in identity_pattern.finditer(data)),('original UDID found; refusing export',p.name)
    tail=data[-65:]"""
        assert source.count(anchor) == 1
        source = source.replace(anchor, replacement, 1).replace('physical_serial_guard_passed=True',
            'physical_serial_guard_passed=True,original_udid_guard_passed=True', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source093(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
