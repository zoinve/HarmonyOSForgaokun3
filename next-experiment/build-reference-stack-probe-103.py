"""Build unchanged HarmonyMac DFX probe against this image's native libraries."""
from pathlib import Path
import hashlib
import json
import posixpath
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
REFERENCE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    work = BUILD/'reference-stack-probe-103'
    report = ROOT/'reports/reference-stack-probe-103'
    assert not work.exists() and not report.exists()
    revision = subprocess.check_output(['git', '-C', str(REFERENCE), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == 'f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad'
    work.mkdir()
    report.mkdir()
    runtime = work/'runtime'
    runtime.mkdir()
    records = []
    def resolve(origin):
        for _ in range(16):
            info = subprocess.check_output(['/usr/sbin/debugfs', '-R', 'stat '+origin, str(IMAGE)], stderr=subprocess.DEVNULL, text=True)
            match = re.search(r'Fast link dest: "([^"]+)"', info)
            if not match:
                return origin
            target = match[1]
            origin = posixpath.normpath(target if target.startswith('/') else posixpath.join(posixpath.dirname(origin), target))
            assert origin.startswith('/') and not origin.startswith('/../')
        raise RuntimeError('symlink loop')
    def extract(name):
        assert '/' not in name
        for directory in ['/system/lib64/chipset-sdk-sp', '/system/lib64/chipset-sdk',
                          '/system/lib64/platformsdk', '/system/lib64/chipset-pub-sdk',
                          '/system/lib64', '/system/lib64/ndk', '/system/lib']:
            origin = directory+'/'+name
            resolved = resolve(origin)
            body = subprocess.check_output(['/usr/sbin/debugfs', '-R', 'cat '+resolved, str(IMAGE)], stderr=subprocess.DEVNULL)
            if body.startswith(b'\x7fELF'):
                path = runtime/name
                path.open('xb').write(body)
                records.append(dict(name=name, image_path=origin, resolved_image_path=resolved, sha256=sha(path)))
                return path
        raise RuntimeError('original library missing: '+name)
    queue = ['libdfx_dumpcatcher.z.so', 'libc++.so', 'libc.so']
    seen = set()
    while queue:
        name = queue.pop(0)
        if name in seen:
            continue
        seen.add(name)
        binary = extract(name)
        dynamic = subprocess.check_output(['aarch64-linux-gnu-readelf', '-d', str(binary)], text=True)
        queue.extend(re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic))
    source = REFERENCE/'ports/tests/app-stack-probe.cpp'
    header = REFERENCE/'ports/tests/include/dfx_dump_catcher.h'
    for path in (source, header):
        shutil.copyfile(path, work/path.name)
    manifest = json.loads((ROOT/'reports/commercial-graphics-014/result.json').read_text())
    command = manifest['commands'][0][:manifest['commands'][0].index('-shared')]
    command += ['-O2', '-Wall', '-Wextra', '-I'+str(work), str(work/source.name),
                str(runtime/'libdfx_dumpcatcher.z.so'), str(runtime/'libc++.so'),
                str(runtime/'libc.so'), '-Wl,-rpath-link,'+str(runtime), '-o', str(work/'app-stack-probe')]
    result = subprocess.run(command, capture_output=True, timeout=120)
    (report/'link.stdout').open('xb').write(result.stdout)
    (report/'link.stderr').open('xb').write(result.stderr)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    assert not any('/sdk/' in line and line.strip().endswith('.so') for line in result.stdout.decode().splitlines())
    assert sha(source) == sha(work/source.name) and sha(header) == sha(work/header.name)
    dynamic = subprocess.check_output(['aarch64-linux-gnu-readelf', '-d', str(work/'app-stack-probe')], text=True)
    assert 'libc++_shared.so' not in dynamic
    result = dict(reference_revision=revision,
                  source_sha256=sha(source), header_sha256=sha(header),
                  source_and_header_byte_identical=True, command=command,
                  original_libraries=records, probe_sha256=sha(work/'app-stack-probe'),
                  native_libraries_from_supplied_image=True, sdk_runtime_libraries_used=False,
                  target_booted=False, target_runtime_verified=False,
                  original_images_modified=False, desktop_verified=False)
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(result, indent=2))
    for path in (work/source.name, work/header.name, work/'app-stack-probe'):
        shutil.copyfile(path, report/path.name)
    print(json.dumps(result, indent=2))
