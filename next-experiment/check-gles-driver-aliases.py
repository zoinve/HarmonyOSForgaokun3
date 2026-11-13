"""Check product-loader aliases point to real Mesa drivers in actual payload."""
from pathlib import Path
import json
import sys

manifest = json.loads(Path(sys.argv[1]).read_text())
files = {row['path']: row for row in manifest['files']}
for alias, target in [('libGLESv1_impl.so', 'libGLESv1_CM.so.1'),
                      ('libGLESv2_impl.so', 'libGLESv2.so.2'),
                      ('libGLESv3_impl.so', 'libGLESv2.so.2')]:
    import hashlib
    entry = files.get('gpu883-libs/' + alias)
    assert entry, 'missing product-loader alias: ' + alias
    assert int(entry['mode'], 8) & 0o170000 == 0o120000
    assert entry['sha256'] == hashlib.sha256(target.encode()).hexdigest()
    assert 'gpu883-libs/' + target in files
assert 'gpu883-libs/libEGL.so' not in files, 'original EGL frontend must win'
assert 'gpu883-libs/libc.so' not in files, 'retain original product libc'
print('PASS: real Mesa GLES driver aliases, original frontend/libc retained')
