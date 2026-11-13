"""Losslessly reconstruct actual captured RGB bytes; never infer a desktop."""
from pathlib import Path
import re,json,hashlib,struct,zlib
def png(raw):
    header=re.match(rb'P6\n(\d+) (\d+)\n255\n',raw)
    assert header
    w,h=int(header[1]),int(header[2]);pixels=raw[header.end():]
    assert len(pixels)==w*h*3
    def chunk(kind,body):
        return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body))
    scanlines=b''.join(b'\0'+pixels[y*w*3:(y+1)*w*3] for y in range(h))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scanlines))+chunk(b'IEND',b'')
def extract(text):
    result=[]
    blocks=re.findall(r'NATIVE_PIXELS013_BEGIN sample=(\d+)[^\n]*\n(.*?)NATIVE_PIXELS013_END bytes=(\d+)',text,re.S)
    for sample,body,count in blocks:
        raw=bytearray()
        for offset,h in re.findall(r'NATIVE_PIXELS013_HEX (\d+) ([0-9a-f]+)',body):
            assert int(offset)==len(raw),'noncontiguous or missing bytes'
            raw.extend(bytes.fromhex(h))
        assert len(raw)==int(count),'truncated capture'
        header=re.match(rb'P6\n(\d+) (\d+)\n255\n',raw)
        assert header and len(raw)==header.end()+int(header[1])*int(header[2])*3,'invalid PPM size'
        result.append((int(sample),bytes(raw)))
    return result
if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent/'reports/native-original-graphics-boot-013'
    runtime=json.loads((root/'runtime-result.json').read_text())
    rows=[]
    for sample,raw in extract((root/'native-logs'/runtime['logs'][-1]['name']).read_bytes().decode(errors='replace')):
        output=root/f'scanout-sample-{sample}.ppm'
        with output.open('xb') as f:f.write(raw)
        with output.with_suffix('.png').open('xb') as f:f.write(png(raw))
        header=re.match(rb'P6\n(\d+) (\d+)\n255\n',raw);pixels=raw[header.end():]
        rows.append(dict(sample=sample,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),size=[int(header[1]),int(header[2])],unique_colors=len({pixels[i:i+3] for i in range(0,len(pixels),3)})))
    assert rows,'no captured images'
    with (root/'scanout-extraction.json').open('x') as f:json.dump(rows,f,indent=2)
    print(json.dumps(rows,indent=2))
