"""User-requested disk cleanup: exact historical images, lossless and verified.

Run locally on Windows; --apply performs the archive, otherwise only inventories.
Never reruns an experiment or removes any log/config/result/original image.
"""
from pathlib import Path
import argparse
import json
import subprocess

BASE = Path(__file__).resolve().parent
PAYLOAD = r'''
from pathlib import Path
import gzip, hashlib, json, os, shutil, stat, time

def sha(p, compressed=False):
    h = hashlib.sha256()
    with (gzip.open(p, 'rb') if compressed else p.open('rb')) as f:
        while b := f.read(4 * 1024 * 1024): h.update(b)
    return h.hexdigest()

def safe(p):
    assert p.is_file() and not p.is_symlink(), str(p)
    assert all(not x.is_symlink() for x in p.parents), str(p)
    assert stat.S_ISREG(p.stat().st_mode)

def unused(p):
    value = str(p)
    for loop in Path('/sys/block').glob('loop*/loop/backing_file'):
        assert loop.read_text().strip() != value, ('loop', value)
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            cmd = (proc/'cmdline').read_bytes()
            assert value.encode() not in cmd, ('process', proc.name, value)
            for fd in (proc/'fd').iterdir():
                try: assert os.readlink(fd) != value, ('fd', proc.name, value)
                except (FileNotFoundError, ProcessLookupError): pass
        except (FileNotFoundError, ProcessLookupError): pass
        except PermissionError: raise RuntimeError('Need root for complete open-file checks')

rows = JOB['rows']
assert len(rows) == 4
root = Path(JOB['root'])
assert root.is_dir() and not root.is_symlink()
report = root/'historical-image-archive-20261112.json'
assert not report.exists(), 'Do not overwrite a completed operation'
for row in rows:
    p = Path(row['path'])
    assert p.parent.parent == root and p.name == 'system-graphics.img'
    safe(p); unused(p)
    assert p.stat().st_size == row['bytes']
    assert not p.with_suffix('.img.gz').exists()
    assert not p.with_suffix('.img.gz.partial').exists()

free_before = shutil.disk_usage(root).free
result = dict(root=str(root), started=time.time(), apply=APPLY,
              free_before=free_before, files=[], evidence_preserved=True)
if APPLY:
    for row in rows:
        p = Path(row['path']); safe(p); unused(p)
        original_stat = p.stat()
        digest = sha(p)
        assert digest == row['sha256'], ('input hash', str(p))
        # Retain and verify every sibling log, config, result and auxiliary file.
        evidence = {str(q): sha(q) for q in p.parent.rglob('*')
                    if q.is_file() and q != p and not q.is_symlink()}
        archive = p.with_suffix('.img.gz')
        partial = p.with_suffix('.img.gz.partial')
        with p.open('rb') as src, partial.open('xb') as dst:
            with gzip.GzipFile(filename=p.name, mode='wb', compresslevel=1,
                               fileobj=dst, mtime=int(original_stat.st_mtime)) as gz:
                shutil.copyfileobj(src, gz, 4 * 1024 * 1024)
            dst.flush(); os.fsync(dst.fileno())
        assert sha(partial, compressed=True) == digest, 'Decompressed hash mismatch'
        current = p.stat()
        assert (current.st_ino, current.st_size, current.st_mtime_ns, current.st_ctime_ns) == (
            original_stat.st_ino, original_stat.st_size, original_stat.st_mtime_ns,
            original_stat.st_ctime_ns), 'Input changed during archiving'
        unused(p)
        assert all(sha(Path(q)) == h for q, h in evidence.items())
        os.rename(partial, archive)
        entry = dict(original=str(p), archive=str(archive), bytes=row['bytes'],
                     original_allocated_bytes=original_stat.st_blocks*512,
                     archive_bytes=archive.stat().st_size,
                     archive_allocated_bytes=archive.stat().st_blocks*512,
                     sha256=digest, gzip_sha256=sha(archive),
                     decompressed_sha256_verified=True,
                     sibling_evidence_sha256=evidence,
                     restore='gzip -dk -- ' + str(archive), removed=False)
        result['files'].append(entry)
        # Journal before removing only the verified, now-redundant expanded copy.
        report.write_text(json.dumps(result, indent=2))
        p.unlink()
        entry['removed'] = True
        assert archive.is_file() and not p.exists()
        result['free_after'] = shutil.disk_usage(root).free
        report.write_text(json.dumps(result, indent=2))
        print(json.dumps(dict(archived=str(p), archive_bytes=entry['archive_bytes'])), flush=True)
result['free_after'] = shutil.disk_usage(root).free
result['finished'] = time.time()
if APPLY: report.write_text(json.dumps(result, indent=2))
print('RESULT_JSON=' + json.dumps(result), flush=True)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--host', choices=['wsl', 'matebook'], required=True)
    args = parser.parse_args()
    if args.host == 'wsl':
        root = '/home/zoinve/harmony-virgl-883'
        command = ['wsl', '-d', 'Debian', '-u', 'root', '--', 'python3', '-']
    else:
        root = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921'
        command = ['ssh', 'matebook', 'sudo -n python3 -']
    rows = []
    for number in [941, 944, 947, 949]:
        manifest = json.loads((BASE/f'official-system-{number}/manifest.json').read_text())
        row = dict(next(x for x in manifest['images'] if Path(x['path']).name == 'system-graphics.img'))
        prefix = 'official-system' if args.host == 'wsl' else 'full-system'
        row['path'] = f'{root}/{prefix}-{number}/system-graphics.img'
        rows.append(row)
    source = 'JOB=' + repr(dict(root=root, rows=rows)) + '\nAPPLY=' + repr(args.apply) + '\n' + PAYLOAD
    completed = subprocess.run(command, input=source, capture_output=True, text=True,
                               encoding='utf-8', timeout=1800)
    if completed.stdout: print(completed.stdout)
    if completed.stderr: print(completed.stderr)
    completed.check_returncode()
    result = json.loads(completed.stdout.split('RESULT_JSON=')[-1])
    if args.apply:
        output = BASE.parent/f'reports/historical-image-archive-20261112-{args.host}.json'
        with output.open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2)


if __name__ == '__main__':
    main()
