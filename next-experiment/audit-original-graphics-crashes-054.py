"""Read-only extraction of real guest crash records; no VM rerun or target writes."""
from pathlib import Path
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parents[1]


def main():
    result = json.loads((BASE / 'reports/baremetal-sdk-original-init-qemu-054/result.json').read_text())
    path = result['scratch_data']['retained_path']
    local = Path('//wsl.localhost/Debian' + path)
    def sha(p):
        with p.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    before = sha(local)
    assert before == result['scratch_data']['after_sha256']
    out = BASE / 'reports/original-graphics-crashes-054'
    out.mkdir()
    names = ['cppcrash-render_service-1003-19700101080113765.log',
             'cppcrash-render_service-1003-19700101080125501.log',
             'cppcrash-render_service-1003-19700101080136642.log']
    files = []
    for name in names:
        cmd = ['wsl', '-d', 'Debian', '--', 'debugfs', '-R',
               'cat /log/faultlog/faultlogger/' + name, path]
        read = subprocess.run(cmd, capture_output=True, check=True, timeout=20)
        assert b'render_service' in read.stdout and len(read.stdout) > 1000
        (out / name).write_bytes(read.stdout)
        (out / (name + '.stderr')).write_bytes(read.stderr)
        files.append(dict(path=name, bytes=len(read.stdout), sha256=hashlib.sha256(read.stdout).hexdigest()))
    assert sha(local) == before
    evidence = dict(scratch_sha256_before_and_after=before, debugfs_readonly=True,
                    vm_rerun=False, original_crash_files=files)
    with (out / 'result.json').open('x') as stream:
        json.dump(evidence, stream, indent=2)
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
