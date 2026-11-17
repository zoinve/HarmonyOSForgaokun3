"""Lossless recompression only; preserve the completed gzip build evidence."""
from pathlib import Path
import gzip
import hashlib
import json
import lzma

base = Path(__file__).resolve().parents[1]
kernel = json.loads((base / 'reports/native-binder-kernel-045/result.json').read_text())
image = Path(kernel['image'])
config = image.parents[3] / '.config'
assert hashlib.sha256(image.read_bytes()).hexdigest() == kernel['sha256']
assert hashlib.sha256(config.read_bytes()).hexdigest() == kernel['config_sha256']
assert 'CONFIG_RD_XZ=y' in config.read_text().splitlines()
work = Path('/home/zoinve/harmony-virgl-883/commercial61-native-072')
report = base / 'reports/commercial61-native-072'
old = json.loads((report / 'overlay-result.json').read_text())
blob = (work / 'minimal-overlay.img').read_bytes()
assert hashlib.sha256(blob).hexdigest() == old['sha256']
data = gzip.decompress(blob)
packed = lzma.compress(data, format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC32,
    filters=[{'id': lzma.FILTER_LZMA2, 'preset': 9, 'dict_size': 8 * 1024 * 1024}])
assert lzma.decompress(packed) == data
assert len(packed) + 32 * 1024 * 1024 < 81068032
with (work / 'minimal-overlay-xz.img').open('xb') as f:
    f.write(packed)
record = dict(old, bytes=len(packed), sha256=hashlib.sha256(packed).hexdigest(),
    compression='xz-crc32', uncompressed_sha256=hashlib.sha256(data).hexdigest(),
    exact_uncompressed_archive_unchanged=True, gzip_sha256=old['sha256'],
    target_kernel_sha256=kernel['sha256'], target_config_sha256=kernel['config_sha256'],
    target_config_rd_xz_verified=True, original_gzip_artifacts_preserved=True)
for target in [work / 'overlay-result-xz.json', report / 'overlay-result-xz.json']:
    with target.open('x') as f:
        json.dump(record, f, indent=2)
print(json.dumps({k: v for k, v in record.items() if k not in ['members', 'chain']}, indent=2))
