"""Extract actual retained guest freeze reports; no target execution or writes."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]


def hash_guest_file(path):
    script = "from pathlib import Path; import hashlib,sys; p=Path(sys.argv[1]); assert p.is_file() and not p.is_symlink() and p.stat().st_size==8589934592; f=p.open('rb'); print(hashlib.file_digest(f,'sha256').hexdigest()); f.close()"
    r = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-c', script, path],
                       capture_output=True, text=True, check=True, timeout=180)
    value = r.stdout.strip()
    assert re.fullmatch('[0-9a-f]{64}', value)
    return value


def main():
    run = json.loads((BASE / 'reports/baremetal-sdk-original-init-qemu-096/result.json').read_text())
    data = run['scratch_data']
    path = data['retained_path']
    assert path == '/home/zoinve/harmony-virgl-883/baremetal-sdk-original-init-qemu-096/scratch-data.ext4'
    assert data['test_only'] and data['freshly_formatted'] and not data['original_userdata_attached']
    before = hash_guest_file(path)
    assert before == data['after_sha256']
    out = BASE / 'reports/original-sceneboard-freezes-096'
    out.mkdir()
    selected = [
        ('/log/faultlog/faultlogger/appfreeze-com.ohos.sceneboard-20020035-19700101080717861.log', 412157),
        ('/log/faultlog/faultlogger/appfreeze-com.ohos.sceneboard-20020035-19700101080840489.log', 540106),
        ('/log/faultlog/faultlogger/appfreeze-com.ohos.sceneboard-20020035-19700101080942441.log', 553733),
        ('/app/el2/100/log/com.ohos.sceneboard/watchdog/freeze/freeze_19700101081037_5087.txt', 2050),
    ]
    files = []
    for guest_path, size in selected:
        cmd = ['wsl', '-d', 'Debian', '--', 'debugfs', '-R', 'cat ' + guest_path, path]
        read = subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        assert len(read.stdout) == size and size < 2 * 1024 * 1024
        assert not any(x in read.stderr.lower() for x in (b'checksum', b'not found', b'corrupt', b'error'))
        name = Path(guest_path).name
        with (out / name).open('xb') as stream:
            stream.write(read.stdout)
        with (out / (name + '.stderr')).open('xb') as stream:
            stream.write(read.stderr)
        files.append(dict(guest_path=guest_path, path=name, bytes=size,
                          sha256=hashlib.sha256(read.stdout).hexdigest(), command=cmd))
    assert hash_guest_file(path) == before
    evidence = dict(scratch_sha256_before_and_after=before, original_scratch_unchanged=True,
                    debugfs_readonly=True, sdk_images_accessed=False, vm_rerun=False,
                    original_freeze_files=files, desktop_verified=False)
    with (out / 'result.json').open('x') as stream:
        json.dump(evidence, stream, indent=2)
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
