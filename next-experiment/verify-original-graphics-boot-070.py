"""Verify immutable original graph; report real Binder reads including failures."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-069.py')))['source']
assert source.count("number='069', tag='069'") == 1
source = source.replace("number='069', tag='069'", "number='070', tag='070'")
old = '''        for pid in pids:
            assert prefix + ('IDENTITY pid=%d Uid:\\t' % pid).encode() + b'\\t'.join([str(uid).encode()] * 4) in raw
            assert prefix + ('DOMAIN pid=%d value=u:r:%s:s0' % (pid, name)).encode() in raw
        identities[name] = dict(pids=pids, uid=uid, domain='u:r:' + name + ':s0')'''
assert source.count(old) == 1
source = source.replace(old, '''        identities[name] = runpy.run_path(str(BASE / 'next-experiment/original-graphics-identity-records-001.py'))['audit_identities'](raw, prefix, pids, uid, name)''')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    observed_binder_mounts = [dict(rc=int(rc), errno=int(error))
        for rc, error in re.findall(rb'GRAPHICS070_BINDER_MOUNT rc=(-?\d+) errno=(\d+) guest_only=1', raw)]
    observed_binder_reads = [dict(sample=int(sample), name=name.decode(),
        bytes=int(size), errno=int(error)) for sample, name, size, error in re.findall(
        rb'GRAPHICS070_BINDER_READ sample=(\d+) name=([A-Za-z0-9_/]+) bytes=(-?\d+) errno=(\d+)', raw)]
    observed_binder_blocks = [dict(sample=int(sample), name=name.decode(),
        text=text.decode(errors='replace')) for sample, name, text in re.findall(
        rb'GRAPHICS070_BINDER_READ sample=(\d+) name=([A-Za-z0-9_/]+) bytes=\d+ errno=0\r?\n(.*?)GRAPHICS070_BINDER_END', raw, re.S)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
        observed_binder_mounts=observed_binder_mounts,
        observed_binder_reads=observed_binder_reads,
        observed_binder_blocks=observed_binder_blocks,
        ''')
compile(source, 'independent-original-graphics-070', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-070', 'exec'))
