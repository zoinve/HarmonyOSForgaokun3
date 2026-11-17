"""Strict decoding of actual captured P6 bytes; never synthesizes frame pixels."""
import hashlib,re
def decode(size,encoded):
    if not 0<size<=131072 or len(encoded)!=size*2:
        raise ValueError('capture byte count mismatch')
    try:blob=bytes.fromhex(encoded)
    except ValueError:raise ValueError('capture is not hexadecimal') from None
    if len(blob)!=size:raise ValueError('capture length mismatch')
    m=re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\n',blob)
    if not m:raise ValueError('not an 8-bit binary RGB PPM')
    width,height=map(int,m.groups())
    if not 0<width<=4096 or not 0<height<=4096 or len(blob)-m.end()!=width*height*3:
        raise ValueError('truncated, oversized or inconsistent frame')
    pixels=blob[m.end():]
    return dict(blob=blob,width=width,height=height,sha256=hashlib.sha256(blob).hexdigest(),
        unique_rgb_colors=len({pixels[i:i+3] for i in range(0,len(pixels),3)}),
        nonblack_pixels=sum(pixels[i:i+3]!=b'\0\0\0' for i in range(0,len(pixels),3)))
