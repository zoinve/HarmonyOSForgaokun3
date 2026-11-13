"""Independently check captured pixels, hashes and the unchanged original guest."""
from pathlib import Path
import hashlib
import runpy
import struct
import zlib


def inspect_frame(ppm, png):
    magic, dimensions, maximum, pixels = ppm.split(b'\n', 3)
    assert magic == b'P6' and maximum == b'255'
    width, height = map(int, dimensions.split())
    assert 0 < width <= 8192 and 0 < height <= 8192
    assert len(pixels) == width * height * 3
    assert png[:8] == b'\x89PNG\r\n\x1a\n'
    position, compressed, header = 8, bytearray(), None
    while position < len(png):
        length = struct.unpack('!I', png[position:position + 4])[0]
        kind = png[position + 4:position + 8]
        body = png[position + 8:position + 8 + length]
        crc = struct.unpack('!I', png[position + 8 + length:position + 12 + length])[0]
        assert zlib.crc32(kind + body) == crc
        if kind == b'IHDR':
            header = struct.unpack('!IIBBBBB', body)
        if kind == b'IDAT':
            compressed.extend(body)
        position += length + 12
    assert position == len(png) and header == (width, height, 8, 2, 0, 0, 0)
    scanlines = zlib.decompress(compressed)
    stride = width * 3 + 1
    assert len(scanlines) == height * stride
    assert all(scanlines[row * stride] == 0 for row in range(height))
    decoded = b''.join(scanlines[row * stride + 1:(row + 1) * stride] for row in range(height))
    assert decoded == pixels
    colors = set()
    nonblack = 0
    for offset in range(0, len(pixels), 3):
        pixel = pixels[offset:offset + 3]
        nonblack += pixel != b'\0\0\0'
        if len(colors) < 4096:
            colors.add(pixel)
    return dict(width=width, height=height, pixel_sha256=hashlib.sha256(pixels).hexdigest(),
                nonblack_pixels=nonblack, distinct_colors_capped_at_4096=len(colors),
                png_lossless_match=True, desktop_verified=False, physical_display=False)


parent = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-074.py')))
source = parent['source']
assert source.count("number='074', tag='074'") == 1
source = source.replace("number='074', tag='074'", "number='075', tag='074'")
anchor = 'print(json.dumps(dict(original_images_independent_hashes=True,'
assert source.count(anchor) == 1
source = source.replace(anchor, '''assert result['initrd_sha256']==json.loads((project/'reports/baremetal-sdk-original-init-qemu-074/result.json').read_text())['initrd_sha256']
for frame in result.get('virtual_scanout_captures',[]):
 if not frame.get('guest_pixels_observed'):continue
 for row in frame['files']:
  p=Path(row['path']);q=project/'reports/baremetal-sdk-original-init-qemu-075'/p.name
  assert p.stat().st_size==q.stat().st_size==row['bytes'] and sha(p)==sha(q)==row['sha256']
''' + anchor)
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    inspect_pixels = runpy.run_path(str(BASE / 'next-experiment/verify-original-graphics-boot-075.py'))['inspect_frame']
    virtual_scanout_verified_frames = []
    for frame in result.get('virtual_scanout_captures', []):
        if not frame.get('guest_pixels_observed'):
            continue
        paths = {Path(row['path']).suffix: BASE / 'reports/baremetal-sdk-original-init-qemu-075' / Path(row['path']).name for row in frame['files']}
        inspected = inspect_pixels(paths['.ppm'].read_bytes(), paths['.png'].read_bytes())
        inspected['elapsed_seconds'] = frame['elapsed_seconds']
        inspected['png_path'] = str(paths['.png'])
        virtual_scanout_verified_frames.append(inspected)
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
         virtual_scanout_verified_frames=virtual_scanout_verified_frames,
         virtual_scanout_capture_results=result.get('virtual_scanout_captures', []),
         ''')
compile(source, 'independent-original-scanout-075', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-scanout-075', 'exec'))
