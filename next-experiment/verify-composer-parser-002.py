"""Read-only independent check of parser evidence and host preservation."""
from pathlib import Path
import hashlib
import importlib.util
import json
import struct
import subprocess

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'reports/composer-parser-002-independent-verification.json'


def main():
    assert not OUT.exists(), OUT
    package = BASE / 'reports/composer-parser-package-001'
    trial = BASE / 'reports/composer-parser-run-002'
    result = json.loads((trial / 'result.json').read_text())
    assert result['returncode'] == 0 and not result['timed_out']
    assert result['before'] == result['after'] and result['host_preserved']
    cmd = result['command']
    assert cmd[cmd.index('-accel') + 1] == 'tcg,thread=multi'
    assert cmd[cmd.index('-display') + 1] == 'none' and '-nodefaults' in cmd
    assert cmd[cmd.index('-nic') + 1] == 'none'
    assert not set(cmd) & {'-drive', '-blockdev', '-device', '-netdev', '-fsdev', '-virtfs', '-hda', '-cdrom'}
    text = (trial / 'serial.log').read_text()
    rows = [s for s in text.splitlines() if s.startswith('PARSER001_CASE ')]
    assert rows == result['cases'] and len(rows) == 8 and all(s.endswith('pass=1') for s in rows)
    assert text.count('PARSER001_PASS cases=8 ') == 1
    assert sum(s.startswith('GPU883_USERSPACE_EXIT child=') and
               ' completed=1 status=0 desktop_not_tested=1' in s
               for s in text.splitlines()) == 1
    assert (trial / 'stderr.log').stat().st_size == 0
    spec = importlib.util.spec_from_file_location('builder', BASE / 'next-experiment/build-composer-parser-001.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    parent = (BASE / 'next-experiment/official-composer-service-957/initramfs.cpio.gz').read_bytes()
    assert hashlib.sha256(parent).hexdigest() == builder.PARENT_HASH
    manifest = json.loads((package / 'manifest.json').read_text())
    body = (package / 'initramfs.cpio.gz').read_bytes()
    assert hashlib.sha256(body).hexdigest() == manifest['initrd_sha256']
    before, after = builder.unpack(parent), builder.unpack(body)
    assert before.keys() == after.keys()
    assert [n for n in before if before[n] != after[n]] == ['gpu-userspace-probe']
    prior = json.loads((BASE / 'reports/composer-smq-001/result.json').read_text())
    service = prior['inputs'][2]
    original = Path('//wsl.localhost/Debian' + service['path']).read_bytes()
    assert hashlib.sha256(original).hexdigest() == service['sha256'] == builder.SERVICE_HASH
    # Resolve original VA through its actual PT_LOAD, not an assumed file offset.
    phoff = struct.unpack_from('<Q', original, 32)[0]
    phsize, phnum = struct.unpack_from('<HH', original, 54)
    def bytes_at(va, count):
        for i in range(phnum):
            typ, _, offset, addr, _, size, _, _ = struct.unpack_from('<IIQQQQQQ', original, phoff + i * phsize)
            if typ == 1 and addr <= va and va + count <= addr + size:
                return original[offset + va - addr:offset + va - addr + count]
        raise AssertionError(hex(va))
    table = bytes_at(0x62f2, 18)
    target = 0x1c834 + table[1] * 4
    assert target == 0x1c884
    assert bytes_at(target + 4, 4) == struct.pack('<I', 0x9400059e)
    old = BASE / 'reports/baremetal-native-trial-012-collected'
    raw = json.loads((old / 'collection.json').read_text())
    for r in raw['files']:
        b = (old / r['path']).read_bytes()
        assert len(b) == r['bytes'] and hashlib.sha256(b).hexdigest() == r['sha256']
    names = ['serial.log', 'stderr.log', 'result.json', 'runner.py']
    local = {n: hashlib.sha256((trial / n).read_bytes()).hexdigest() for n in names}
    payload = 'expected=' + repr(local) + '\nexpected_boot=' + repr(result['before']['boot_id']) + '\n' + r'''
from pathlib import Path
import hashlib,json,os,runpy,subprocess
o=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/composer-parser-runtime-002')
assert {n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in expected}==expected
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==expected_boot
assert os.uname().release=='7.1.0-rc3-gaokun3+'
def ro(args,**kw):
    assert 'set-property' not in args
    return subprocess.run(args,**kw)
rows=runpy.run_path('/usr/local/libexec/harmony-lab-screen-off-001.py')['run_once'](runner=ro)
assert rows and all(r['state']=='off' and not r['changed'] for r in rows),rows
v=Path('/sys/firmware/efi/efivars');g='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f'
d=(v/('LoaderEntryDefault-'+g)).read_bytes()[4:].decode('utf-16-le').rstrip('\0')
assert d=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
one=v/('LoaderEntryOneShot-'+g)
assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
assert not list(Path('/boot/efi/loader/entries').glob('harmony-native-diag-*.conf'))
print(json.dumps(dict(remote_artifact_hashes=expected,boot_id=expected_boot,
                     screen_rows=rows,screen_changed=False,physical_screen_observed=False,
                     persistent_default=d,one_shot_absent=True)))
'''
    p = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=payload,
                       text=True, capture_output=True, timeout=90)
    assert p.returncode == 0, p.stderr
    verified = dict(cases_verified=len(rows), original_records_unchanged=len(before) - 1,
                    prior_native_logs_verified=len(raw['files']), remote=json.loads(p.stdout),
                    dispatch_0x41=dict(table_va='0x62f2', table_byte=table[1],
                                       thunk_va=hex(target), handler_va='0x1df00'),
                    parser_only=True, smq_verified=False, desktop_verified=False)
    with OUT.open('x') as f:
        json.dump(verified, f, indent=2)
    print(json.dumps(verified, indent=2))


if __name__ == '__main__':
    main()
