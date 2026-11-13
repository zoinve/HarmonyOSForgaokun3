"""Extract existing guest HiLog evidence read-only; never starts a VM."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parents[1]


def main():
    run = json.loads((BASE / 'reports/baremetal-sdk-original-init-qemu-054/result.json').read_text())
    scratch = run['scratch_data']['retained_path']
    local = Path('//wsl.localhost/Debian' + scratch)
    def sha():
        with local.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    before = sha()
    assert before == run['scratch_data']['after_sha256']
    out = BASE / 'reports/original-graphics-hilog-054'
    out.mkdir()
    files = []
    for name in ['hilog.000.19700101-080019.gz', '.dict_info.json', 'hilog_diag.log']:
        proc = subprocess.run(['wsl', '-d', 'Debian', '--', 'debugfs', '-R',
                               'cat /log/hilog/' + name, scratch],
                              capture_output=True, check=True, timeout=30)
        assert proc.stdout
        (out / name).open('xb').write(proc.stdout)
        (out / (name + '.stderr')).open('xb').write(proc.stderr)
        files.append(dict(path=name, bytes=len(proc.stdout), sha256=hashlib.sha256(proc.stdout).hexdigest()))
        if name.endswith('.gz'):
            raw = gzip.decompress(proc.stdout)
            (out / 'hilog.decompressed').open('xb').write(raw)
            files.append(dict(path='hilog.decompressed', bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    assert sha() == before
    evidence = dict(files=files, scratch_sha256_before_and_after=before, debugfs_readonly=True, vm_rerun=False)
    (out / 'result.json').open('x').write(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
