"""Read-only QMP status/scanout capture and lossless PPM-to-PNG conversion."""
from pathlib import Path
import hashlib
import json
import re
import socket
import struct
import time
import zlib


def decode_ppm(body):
    match = re.match(rb'^P6\s+(\d+)\s+(\d+)\s+255\s', body)
    if not match:
        raise ValueError('unsupported PPM header')
    width, height = map(int, match.groups())
    if not (0 < width <= 8192 and 0 < height <= 8192):
        raise ValueError('bounded dimensions required')
    pixels = body[match.end():]
    if len(pixels) != width * height * 3:
        raise ValueError('incomplete PPM pixels')
    return width, height, pixels


def encode_png(width, height, pixels):
    if len(pixels) != width * height * 3:
        raise ValueError('wrong pixel count')

    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))

    rows = b''.join(b'\0' + pixels[i * width * 3:(i + 1) * width * 3] for i in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def capture_frame(socket_path, ppm_path):
    path = Path(ppm_path)
    png_path = path.with_suffix('.png')
    if path.exists() or png_path.exists():
        raise FileExistsError('capture paths must be new')
    deadline = time.monotonic() + 12
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(8)
        connection.connect(str(socket_path))
        stream = connection.makefile('rwb', buffering=0)

        def receive():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('bounded QMP capture deadline')
            connection.settimeout(remaining)
            line = stream.readline(1024 * 1024)
            if not line or len(line) >= 1024 * 1024:
                raise ValueError('missing or oversized QMP response')
            return json.loads(line)

        def request(name, identity, arguments=None):
            if name not in ('qmp_capabilities', 'query-status', 'screendump'):
                raise ValueError('observation-only QMP command required')
            message = dict(execute=name, id=identity)
            if arguments is not None:
                message['arguments'] = arguments
            stream.write(json.dumps(message).encode() + b'\r\n')
            for _ in range(128):
                response = receive()
                if response.get('id') == identity:
                    if 'error' in response:
                        raise RuntimeError(json.dumps(response['error']))
                    return response['return']
            raise ValueError('too many unrelated QMP events')

        if 'QMP' not in receive():
            raise ValueError('missing QMP greeting')
        request('qmp_capabilities', 'capabilities')
        status = request('query-status', 'status')
        request('screendump', 'frame', dict(filename=str(path)))
    width, height, pixels = decode_ppm(path.read_bytes())
    with png_path.open('xb') as output:
        output.write(encode_png(width, height, pixels))
    return dict(status=status, width=width, height=height,
                files=[dict(path=str(p), bytes=p.stat().st_size,
                            sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (path, png_path)],
                guest_pixels_observed=True, desktop_verified=False, physical_display=False)
