"""Unique 092 evidence with unchanged core and explicit early-entry selection."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
previous = runpy.run_path(str(BASE/'commercial-workflow-091.py'))
configure_local_transport = previous['configure_local_transport']


def source092(name):
    source = previous['source091'](name).replace('commercial61-native-091', 'commercial61-native-092').replace(
        'commercial-return-audit-091', 'commercial-return-audit-092').replace(
        'ordered_chain_equals_full_091', 'ordered_chain_equals_full_092').replace(
        'retain-commercial-entries-091.py', 'retain-commercial-entries-092.py').replace(
        'Original hardware identity input 091', 'Real early hardware model input 092')
    if name == 'install-commercial-native':
        assert all(json.loads((BASE.parent/'reports/commercial61-native-092/admission-test.json').read_text()).values())
        parent = json.loads((BASE.parent/'reports/commercial61-native-091/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        replacements = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-092/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-092/initrd.img']),
            "assert sha(esp/'commercial61-native-090/initrd.img')==" + repr(old):
                "assert sha(esp/'commercial61-native-090/initrd.img')==" + repr(old) +
                "\nassert sha(esp/'commercial61-native-091/initrd.img')==" + repr(parent['sha256']),
            "'initrd /commercial61-native-090/initrd.img','initrd /commercial61-native-092/initrd.img'":
                "'initrd /commercial61-native-090/initrd.img','initrd /commercial61-native-091/initrd.img','initrd /commercial61-native-092/initrd.img'",
            "options=next(x for x in old.splitlines() if x.startswith('options ')).replace('panic=0','panic=15')+' harmony.commercial=1'":
                "options=next(x for x in old.splitlines() if x.startswith('options ')).replace('panic=0','panic=15')+' harmony.commercial=1'\nassert options.count('rdinit=/init ')==1\noptions=options.replace('rdinit=/init ', 'rdinit=/early-hardware092.sh ', 1)",
        }
        for anchor, replacement in replacements.items():
            assert source.count(anchor) == 1, anchor
            source = source.replace(anchor, replacement, 1)
    if name == 'retrieve-commercial-evidence':
        runs = [json.loads((BASE.parent/f'reports/commercial61-native-{n}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                for n in ('087', '088', '089', '090', '091')]
        anchor = 'if p.name not in ' + repr(runs[:4])
        assert source.count(anchor) == 1
        source = source.replace(anchor, 'if p.name not in ' + repr(runs), 1)
        anchor = ' files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in run.iterdir() if p.is_file()}'
        guard = ''' serials=[Path('/sys/class/dmi/id/'+key).read_bytes().strip() for key in ('product_serial','chassis_serial')]
 assert all(len(value)==16 and value.isalnum() for value in serials)
 needles=set(value for serial in serials for value in (serial,serial.lower(),serial.upper()))
 for p in run.iterdir():
  if not p.is_file():continue
  with p.open('rb') as stream:
   tail=b''
   while chunk:=stream.read(1024*1024):
    data=tail+chunk
    assert not any(value in data for value in needles),('physical serial found; refusing export',p.name)
    tail=data[-15:]
'''
        assert source.count(anchor) == 1
        source = source.replace(anchor, guard + anchor, 1).replace(
            'files=files,read_only_noload=True', 'files=files,read_only_noload=True,physical_serial_guard_passed=True', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source092(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
