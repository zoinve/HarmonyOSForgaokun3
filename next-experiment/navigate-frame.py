"""Throwaway headless keyboard/framebuffer diagnostic for observer payload 913."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import zlib

number = int(sys.argv[1])
assert number >= 914
label = sys.argv[2]
keys = sys.argv[3:]
assert label.replace('-', '').isalnum()
assert all(k in ('tab', 'ret', 'esc', 'spc') for k in keys)
out = Path(__file__).parent / f'run-{number}'
assert not (out / (label + '.png')).exists()
script = r'''
import socket,json,time,subprocess
from pathlib import Path
p=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-EXPERIMENT')
s=socket.socket(socket.AF_UNIX);s.settimeout(8);s.connect(str(p/'qmp.sock'));f=s.makefile('rwb',buffering=0);f.readline()
def q(c,a=None):
 f.write((json.dumps({'execute':c,**({'arguments':a} if a else {})})+'\n').encode())
 while True:
  r=json.loads(f.readline())
  if 'return' in r or 'error' in r:
   assert 'error' not in r,r
   return r
q('qmp_capabilities');print(q('query-status'))
for key in KEYS:
 for down in (True,False):
  q('input-send-event',{'events':[{'type':'key','data':{'down':down,'key':{'type':'qcode','data':key}}}]});time.sleep(.12)
 time.sleep(.3)
time.sleep(35)
dst=p/(LABEL+'.ppm');assert not dst.exists()
r=subprocess.run(['debugfs','-n','-R',f'dump /local/tmp/gpu913-capture/latest.ppm {dst}',str(p/'userdata-permissive.img')],capture_output=True,text=True)
print(r.stderr);assert dst.stat().st_size>6000000
print('\n'.join(x for x in (p/'serial.log').read_text(errors='replace').splitlines() if 'GPU913_CAPTURE' in x)[-300:])
'''.replace('KEYS', repr(keys)).replace('LABEL', repr(label)).replace('EXPERIMENT', str(number))
r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=script,
                   text=True, capture_output=True, check=True, timeout=65)
print(r.stdout, r.stderr)
subprocess.run(['scp', f'matebook:/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-{number}/' + label + '.ppm', str(out / (label + '.ppm'))], check=True)
b = (out / (label + '.ppm')).read_bytes()
head, wh, mx, pix = b.split(b'\n', 3)
w, h = map(int, wh.split())
assert head == b'P6' and mx == b'255' and len(pix) == w*h*3
def chunk(t, d):
    return struct.pack('>I', len(d))+t+d+struct.pack('>I', zlib.crc32(t+d)&0xffffffff)
png = b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
png += chunk(b'IDAT', zlib.compress(b''.join(b'\0'+pix[y*w*3:(y+1)*w*3] for y in range(h))))+chunk(b'IEND',b'')
(out / (label + '.png')).write_bytes(png)
print(out / (label + '.png'))
