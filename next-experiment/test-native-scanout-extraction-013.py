"""Exercise contiguous byte reconstruction and reject truncation/corruption."""
from pathlib import Path
import runpy
if __name__=='__main__':
    p=Path(__file__).with_name('extract-native-scanout-013.py')
    assert p.exists(),'missing lossless scanout extractor'
    module=runpy.run_path(str(p));extract=module['extract']
    raw=b'P6\n1 1\n255\n\x01\x02\x03'
    text='NATIVE_PIXELS013_BEGIN sample=9 fd=3 errno=0\nNATIVE_PIXELS013_HEX 0 '+raw.hex()+'\nNATIVE_PIXELS013_END bytes='+str(len(raw))
    assert extract(text)==[(9,raw)]
    for bad in [text.replace('HEX 0','HEX 1'),text.replace('bytes='+str(len(raw)),'bytes=1')]:
        try:extract(bad)
        except AssertionError:pass
        else:raise AssertionError('corrupt frame accepted')
    assert 'png' in module,'missing dependency-free PNG encoder'
    import zlib,struct
    data=module['png'](raw);assert data[:8]==b'\x89PNG\r\n\x1a\n'
    offset=8;decoded=b''
    while offset<len(data):
        count=struct.unpack_from('>I',data,offset)[0];kind=data[offset+4:offset+8]
        if kind==b'IDAT':decoded+=zlib.decompress(data[offset+8:offset+8+count])
        offset+=12+count
    assert decoded==b'\x00\x01\x02\x03'
    print('lossless roundtrip, RGB PNG encoding and two corruption rejections passed')
