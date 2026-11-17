"""Host parser fixtures only, never target service or desktop success evidence."""
from pathlib import Path
import subprocess
import tempfile

base = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='commercial-binder043-') as directory:
    binary = Path(directory) / 'parser-test'
    subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(base / 'test-commercial-binder-observer-043.cpp'),
                    '-o', str(binary)], check=True, timeout=60)
    subprocess.run([str(binary)], check=True, timeout=20)
print('PASS: public Binder64 transaction/SG parsing, descriptor bounds, capacity, consumed data, truncation, immutable bytes')
