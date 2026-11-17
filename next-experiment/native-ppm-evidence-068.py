"""Read the capture writer's exact P6 schema and encode lossless PNG views."""
from collections import Counter
import re
import struct
import zlib


def parse_ppm(data):
    header = re.match(rb'P6\n([1-9]\d*) ([1-9]\d*)\n255\n', data)
    assert header, 'Not the original capture writer P6 format'
    width, height = map(int, header.groups())
    assert width <= 4096 and height <= 4096
    pixels = data[header.end():]
    assert len(pixels) == width * height * 3, 'Truncated or trailing pixel data'
    return width, height, pixels


def pixel_stats(width, height, pixels):
    assert len(pixels) == width * height * 3
    nonblack = 0
    left, top, right, bottom = width, height, -1, -1
    palette = Counter()
    capped = False
    for i in range(width * height):
        pixel = pixels[i*3:i*3+3]
        if pixel != b'\0\0\0':
            nonblack += 1
            y, x = divmod(i, width)
            left, top, right, bottom = min(left, x), min(top, y), max(right, x), max(bottom, y)
        if pixel in palette or len(palette) < 4096:
            palette[pixel] += 1
        else:
            capped = True
    return dict(width=width, height=height, total_pixels=width*height,
                nonblack_pixels=nonblack, nonblack_fraction=nonblack/(width*height),
                nonblack_bbox=[left, top, right, bottom] if nonblack else None,
                histogram_capped=capped,
                palette=[dict(rgb=list(color), pixels=count) for color, count in palette.most_common(16)])


def png_bytes(width, height, pixels):
    assert len(pixels) == width * height * 3

    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name+data))

    scanlines = b''.join(b'\0' + pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(scanlines)) + chunk(b'IEND', b''))
