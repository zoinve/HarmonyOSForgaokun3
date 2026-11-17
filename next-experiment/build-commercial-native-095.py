"""Add one guarded normal-close diagnostic without changing original services."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')

if __name__ == '__main__':
    work, report = BUILD/'commercial61-native-095', ROOT/'reports/commercial61-native-095'
    assert not work.exists() and not report.exists()
    tests = json.loads((ROOT/'reports/native-normal-close-095-tests-r2.json').read_text())
    sha = lambda body: hashlib.sha256(body).hexdigest()
    assert tests['source_sha256'] == sha((BASE/'native-normal-close-095.c').read_bytes())
    assert tests['focus_guard_sha256'] == sha((BASE/'commercial-focus-095.awk').read_bytes())
    assert all(item.get('accepted') == item.get('expected') for item in tests['tests'].values() if 'accepted' in item)
    work.mkdir()
    report.mkdir()
    command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
               str(BASE/'native-normal-close-095.c'), '-o', str(work/'native-normal-close095')]
    compiled = subprocess.run(command, capture_output=True)
    (report/'compile.stdout').open('xb').write(compiled.stdout)
    (report/'compile.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr
    helper = (work/'native-normal-close095').read_bytes()
    assert sha(helper) == tests['tests']['aarch64']['binary_sha256']
    tested = subprocess.check_output(['qemu-aarch64', str(work/'native-normal-close095'), '--self-test'])
    assert b'sequence=pass failed_write=pass' in tested
    (report/'helper-self-test.stdout').open('xb').write(tested)
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/'commercial61-native-094/initrd.img').read_bytes()))}
    after = dict(before)
    focus = (BASE/'commercial-focus-095.awk').read_bytes()
    worker = (BASE/'commercial-normal-close-095.sh').read_text().replace('HELPER_SHA', sha(helper)).replace('FOCUS_SHA', sha(focus)).encode()
    additions = {
        'native-target/native-normal-close095': (0o100755, helper),
        'native-target/commercial-focus095.awk': (0o100644, focus),
        'native-target/commercial-normal-close095.sh': (0o100755, worker),
    }
    assert not (set(additions) & set(before))
    after.update(additions)
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/id\n'
    assert before[key][1].count(anchor) == 1
    after[key] = (before[key][0], before[key][1].replace(anchor,
        anchor+b'/system/bin/sh /commercial-normal-close095.sh &\n', 1))
    assert {n for n in before if before[n] != after[n]} == {key}
    previous = json.loads((ROOT/'reports/commercial61-native-094/result.json').read_text())
    for item in previous['artifacts']:
        if item['name'] == 'initrd.img':
            continue
        path = BUILD/'commercial61-native-094'/item['name']
        assert sha(path.read_bytes()) == item['sha256']
        shutil.copyfile(path, work/item['name'])
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    names = [i['name'] for i in previous['artifacts']] + ['native-normal-close095']
    previous['artifacts'] = [dict(name=n, bytes=(work/n).stat().st_size, sha256=sha((work/n).read_bytes())) for n in names]
    previous['normal_window_close_diagnostic'] = dict(helper_sha256=sha(helper), focus_sha256=sha(focus),
        worker_sha256=sha(worker), exact_original_keyboard_required=True, focused_guide_required=True,
        physical_keys_must_be_released=True, one_alt_f4_only=True, original_cores_unchanged=True,
        original_oobe_and_provisioning_unchanged=True, normal_close_not_yet_verified=True)
    previous['runtime_verified'] = False
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    (report/'diagnostic095.sh').open('xb').write(after[key][1])
    (report/'normal-close095.sh').open('xb').write(worker)
    shutil.copyfile(ROOT/'reports/commercial61-native-094/config-provenance.json', report/'config-provenance.json')
    print(json.dumps(previous['normal_window_close_diagnostic'], indent=2))
