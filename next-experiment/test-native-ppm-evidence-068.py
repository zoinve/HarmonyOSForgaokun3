from pathlib import Path
import runpy
import struct
import zlib

h = runpy.run_path(str(Path(__file__).with_name('native-ppm-evidence-068.py')))
pixels = bytes([0,0,0, 2,3,4, 0,0,0, 8,9,10, 0,0,0, 8,9,10])
ppm = b'P6\n3 2\n255\n' + pixels
assert h['parse_ppm'](ppm) == (3,2,pixels)
for bad in [ppm[:-1], ppm+b'x', ppm.replace(b'3 2', b'0 2'), ppm.replace(b'255', b'256')]:
    try:
        h['parse_ppm'](bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('Malformed PPM accepted')
stats = h['pixel_stats'](3,2,pixels)
assert stats['nonblack_pixels'] == 3 and stats['nonblack_bbox'] == [0,0,2,1]
assert not stats['histogram_capped']
png = h['png_bytes'](3,2,pixels)
assert png[:8] == b'\x89PNG\r\n\x1a\n'
offset = 8
compressed = b''
names = []
while offset < len(png):
    length = struct.unpack('>I', png[offset:offset+4])[0]
    name = png[offset+4:offset+8]
    data = png[offset+8:offset+8+length]
    crc = struct.unpack('>I', png[offset+8+length:offset+12+length])[0]
    assert zlib.crc32(name+data) == crc
    names.append(name)
    if name == b'IDAT':
        compressed += data
    offset += length+12
assert offset == len(png) and names == [b'IHDR', b'IDAT', b'IEND']
assert zlib.decompress(compressed) == b'\0'+pixels[:9]+b'\0'+pixels[9:]
print('Exact P6 parsing, full pixel counts, lossless PNG/CRC tests passed')
