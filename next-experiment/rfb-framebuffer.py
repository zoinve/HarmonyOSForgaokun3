"""Read a real framebuffer through a private Unix RFB socket, without input."""
def capture_rfb(directory, target):
    import socket
    import struct
    import hashlib
    with socket.socket(socket.AF_UNIX) as v:
        v.settimeout(10)
        v.connect(str(directory/'vnc.sock'))
        def readn(n):
            data=b''
            while len(data)<n:
                chunk=v.recv(n-len(data))
                assert chunk,'RFB closed'
                data+=chunk
            return data
        assert readn(12).startswith(b'RFB 003.')
        v.sendall(b'RFB 003.008\n')
        types=readn(readn(1)[0]);assert 1 in types,types
        v.sendall(b'\x01');assert readn(4)==b'\0'*4
        v.sendall(b'\x01')
        header=readn(24);w,h=struct.unpack('>HH',header[:4])
        assert 0<w<=4096 and 0<h<=4096,(w,h)
        readn(struct.unpack('>I',header[20:24])[0])
        v.sendall(b'\x00\0\0\0'+struct.pack('>BBBBHHHBBB3x',32,24,0,1,255,255,255,16,8,0))
        v.sendall(struct.pack('>BBHi',2,0,1,0))
        v.sendall(struct.pack('>BBHHHH',3,0,0,0,w,h))
        kind=readn(1)[0];assert kind==0,kind
        count=struct.unpack('>H',readn(3)[1:])[0]
        frame=bytearray(w*h*3)
        coverage=bytearray(w*h)
        for _ in range(count):
            x,y,rw,rh,encoding=struct.unpack('>HHHHi',readn(12))
            assert encoding==0 and x+rw<=w and y+rh<=h,(x,y,rw,rh,encoding)
            data=readn(rw*rh*4)
            for yy in range(rh):
                a=yy*rw*4;b=((y+yy)*w+x)*3
                row=data[a:a+rw*4]
                rgb=bytearray(rw*3)
                rgb[0::3]=row[2::4];rgb[1::3]=row[1::4];rgb[2::3]=row[0::4]
                frame[b:b+rw*3]=rgb
                coverage[(y+yy)*w+x:(y+yy)*w+x+rw]=b'\x01'*rw
        assert all(coverage),'Incomplete nonincremental framebuffer'
        target.write_bytes(('P6\n%d %d\n255\n'%(w,h)).encode()+frame)
        return dict(name=target.name,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),width=w,height=h,nonblack_pixels=sum(any(frame[i:i+3]) for i in range(0,len(frame),3)),rfb_rectangles=count)
