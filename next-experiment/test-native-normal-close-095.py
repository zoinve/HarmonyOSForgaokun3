"""Exercise normal-close byte sequence and original WM table guards off-device."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    out = ROOT/'reports/native-normal-close-095-tests-r2.json'
    assert not out.exists()
    source = BASE/'native-normal-close-095.c'
    awk = BASE/'commercial-focus-095.awk'
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    archive = Path('/home/zoinve/harmony-virgl-883/commercial61-native-094/initrd.img')
    members = {name: body for name, mode, body in parse(gzip.decompress(archive.read_bytes()))}
    results = {}
    with tempfile.TemporaryDirectory(prefix='normal-close095-') as temporary:
        work = Path(temporary)
        busybox = work/'busybox'
        busybox.write_bytes(members['bin/busybox'])
        busybox.chmod(0o755)
        for compiler, runner, name in [('gcc', [], 'host'), ('aarch64-linux-gnu-gcc', ['qemu-aarch64'], 'aarch64')]:
            binary = work/name
            subprocess.run([compiler, '-static', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(binary)], check=True)
            result = subprocess.run(runner+[str(binary), '--self-test'], capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, result.stderr
            assert 'sequence=pass failed_write=pass' in result.stdout
            invalid = subprocess.run(runner+[str(binary)], capture_output=True, timeout=10)
            assert invalid.returncode == 64
            results[name] = dict(self_test=result.stdout.strip(), invalid_arguments_refused=True,
                                 binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
        header = 'WindowName DisplayId Pid WinId Type Mode Flag ZOrd Orientation\n'
        row = 'hwstartupguide0 0 6468 8 1 1 0 -1 0 [ 0 0 2560 1600 ]\n'
        focus = 'Focus window: 8\n'
        fixtures = {
            'guide-focus': (header+row+focus, '6468', True),
            'desktop-focus': (header+row+'SCBDesktop4 0 4216 7 2001 1 0 -1 0\nFocus window: 7\n', '6468', False),
            'wrong-pid': (header+row+focus, '7777', False),
            'multi-pid': (header+row+focus, '6468 7777', False),
            'missing-focus': (header+row, '6468', False),
            'duplicate-focus': (header+row+focus+focus, '6468', False),
            'duplicate-id': (header+row+row+focus, '6468', False),
            'missing-header': (row+focus, '6468', False),
            'wrong-header': (header.replace('Pid WinId', 'WinId Pid')+row+focus, '6468', False),
            'other-display': (header+row.replace('guide0 0 ', 'guide0 1 ')+focus, '6468', False),
            'wrong-type': (header+row.replace('6468 8 1 ', '6468 8 2001 ')+focus, '6468', False),
            'crlf': ((header+row+focus).replace('\n','\r\n'), '6468', False),
        }
        for name, (text, pid, expected) in fixtures.items():
            result = subprocess.run(['qemu-aarch64', str(busybox), 'awk', '-v', 'guide='+pid, '-f', str(awk)],
                                    input=text, text=True, capture_output=True, timeout=10)
            assert (result.returncode == 0) == expected, (name, result.stdout, result.stderr)
            assert expected or not result.stdout, name
            results[name] = dict(accepted=result.returncode == 0, expected=expected)
    report = dict(tests=results, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  focus_guard_sha256=hashlib.sha256(awk.read_bytes()).hexdigest(),
                  target_busybox_sha256=hashlib.sha256(members['bin/busybox']).hexdigest(),
                  target_keyboard_opened=False, target_booted=False, native_close_verified=False)
    out.open('x').write(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
