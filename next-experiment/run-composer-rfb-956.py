"""Request actual framebuffer readback from Unix-only VNC on the unchanged GL fixture."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
parent = base / 'official-composer-kms-952'
out = base / 'official-composer-rfb-956'
assert not out.exists()
source = (base / 'run-composer-kms-952.py').read_text()
source = source.replace("out = base / 'official-composer-kms-952'", "out = base / 'official-composer-rfb-956'")
source = source.replace('composer-kms-runtime-952', 'composer-rfb-runtime-956')
anchor = "gpu='/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883'"
assert source.count(anchor) == 1
source = source.replace(anchor, "cmd += ['-vnc', 'unix:'+str(o/'vnc.sock')]\n" + anchor)
old = "   request(dict(execute='screendump',arguments=dict(filename=str(o/'kms-test-pattern.ppm'))))"
assert source.count(old) == 1
new = '''    import struct
    with socket.socket(socket.AF_UNIX) as v:
     v.settimeout(7);v.connect(str(o/'vnc.sock'))
     def readn(n):
      data=b''
      while len(data)<n:
       chunk=v.recv(n-len(data));assert chunk,'RFB closed';data+=chunk
      return data
     result['rfb_version']=readn(12).decode();v.sendall(b'RFB 003.008\\n')
     types=readn(readn(1)[0]);assert 1 in types,types;v.sendall(b'\\x01')
     assert readn(4)==b'\\0'*4;v.sendall(b'\\x01')
     header=readn(24);w,h=struct.unpack('>HH',header[:4]);name=readn(struct.unpack('>I',header[20:24])[0])
     result['rfb_initial_size']=[w,h]
     # Explicit 32-bit little-endian RGB, raw rectangles only.
     fmt=struct.pack('>BBBBHHHBBB3x',32,24,0,1,255,255,255,16,8,0)
     v.sendall(b'\\x00\\0\\0\\0'+fmt)
     v.sendall(struct.pack('>BBHi',2,0,1,0))
     v.sendall(struct.pack('>BBHHHH',3,0,0,0,w,h))
     kind=readn(1)[0];assert kind==0,kind
     count=struct.unpack('>H',readn(3)[1:])[0];frame=bytearray(w*h*3)
     for _ in range(count):
      x,y,rw,rh,encoding=struct.unpack('>HHHHi',readn(12));assert encoding==0,encoding
      data=readn(rw*rh*4)
      for yy in range(rh):
       for xx in range(rw):
        a=(yy*rw+xx)*4;b=((y+yy)*w+x+xx)*3
        frame[b:b+3]=bytes((data[a+2],data[a+1],data[a]))
     bad=sum(tuple(frame[(y*w+x)*3:(y*w+x)*3+3]) != (255 if 2+x*9//w<6 else 0,255 if 1+y*5//h<3 else 0,64) for y in range(h) for x in range(w))
     result.update(rfb_rectangles=count,rfb_pixel_mismatches=bad,rfb_pattern_verified=(count>0 and bad==0))
     (o/'kms-test-pattern.ppm').write_bytes(('P6\\n%d %d\\n255\\n'%(w,h)).encode()+frame)'''
new = '\n'.join(line[1:] if line.startswith(' ') else line for line in new.splitlines())
source = source.replace(old, new)
compile(source, 'composer-rfb-956', 'exec')
out.mkdir()
for name in ('manifest.json', 'initramfs.cpio.gz'):
    (out / name).write_bytes((parent / name).read_bytes())
exec(compile(source, 'composer-rfb-956', 'exec'))
