"""Verify native library loading without asking DFX to inspect any process."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WORK = Path('/home/zoinve/harmony-virgl-883/reference-stack-probe-103')


if __name__ == '__main__':
    report = ROOT/'reports/reference-stack-probe-103'
    output = report/'load-tests.json'
    assert not output.exists()
    manifest = json.loads((report/'result.json').read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(WORK/'app-stack-probe') == manifest['probe_sha256']
    for row in manifest['original_libraries']:
        assert sha(WORK/'runtime'/row['name']) == row['sha256']
    tests = []
    with tempfile.TemporaryDirectory(prefix='reference-stack103-load-') as temp:
        folder = Path(temp)
        for source, name in [(WORK/'runtime/libc.so', 'loader'), (WORK/'app-stack-probe', 'probe')]:
            shutil.copyfile(source, folder/name)
            (folder/name).chmod(0o755)
        prefix = ['qemu-aarch64', str(folder/'loader'), '--library-path', str(WORK/'runtime'), str(folder/'probe')]
        for args in [[], ['0'], ['1'], ['-1'], ['0', 'all']]:
            run = subprocess.run(prefix+args, capture_output=True, timeout=25)
            tests.append(dict(arguments=args, status=run.returncode,
                              stdout=run.stdout.decode(errors='replace'), stderr=run.stderr.decode(errors='replace')))
        result = dict(probe_sha256=manifest['probe_sha256'], tests=tests,
                      all_invalid_pid_cases_return_2=all(t['status'] == 2 for t in tests),
                      no_process_dump_requested=True, target_booted=False,
                      original_native_library_graph_hashes_verified=True,
                      target_runtime_verified=False, desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    assert result['all_invalid_pid_cases_return_2']
