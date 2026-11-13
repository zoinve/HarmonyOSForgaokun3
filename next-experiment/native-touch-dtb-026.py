"""Target-copy-only FDT adjustment: rotate genuine touch coordinates into logical display."""
import struct
def records(blob):
    h=list(struct.unpack_from('>10I',blob));assert h[0]==0xd00dfeed and h[1]<=len(blob)
    assert h[5]>=17 and 40<=h[4]<h[2] and h[2]+h[9]<=h[1] and h[3]+h[8]<=h[1]
    strings=blob[h[3]:h[3]+h[8]];i=h[2];limit=i+h[9];stack=[];out=[]
    while i<limit:
        start=i;token=struct.unpack_from('>I',blob,i)[0];i+=4;key=None;data=None
        if token==1:
            end=blob.index(b'\0',i,limit);stack.append(blob[i:end].decode());i=(end+4)&~3
        path='/'+'/'.join(n for n in stack if n)
        if token==3:
            length,offset=struct.unpack_from('>2I',blob,i);i+=8
            assert offset<len(strings) and i+length<=limit
            key=strings[offset:strings.index(b'\0',offset)].decode();data=blob[i:i+length];i=(i+length+3)&~3
        elif token==2:assert stack;stack.pop()
        elif token==9:assert not stack
        else:assert token in (1,4),token
        out.append((token,path,key,data,blob[start:i]))
        if token==9:break
    assert out[-1][0]==9
    return h,strings,out
def properties(blob):return {(p,k):d for t,p,k,d,raw in records(blob)[2] if t==3}
def landscape_dtb(blob):
    h,strings,items=records(blob);before=properties(blob)
    nodes=[p for (p,k),d in before.items() if k=='compatible' and b'himax,hx83121a-ts' in d.split(b'\0')]
    assert len(nodes)==1;node=nodes[0]
    assert before[node,'touchscreen-size-x']==struct.pack('>I',2560)
    assert before[node,'touchscreen-size-y']==struct.pack('>I',1600)
    assert (node,'touchscreen-swapped-x-y') in before
    assert before[node,'touchscreen-swapped-x-y']==b'' and before[node,'touchscreen-inverted-x']==b''
    assert (node,'touchscreen-inverted-y') not in before
    new_name=b'touchscreen-inverted-y\0';offset=len(strings);strings+=new_name
    body=[]
    for token,path,key,data,raw in items:
        if path==node and key=='touchscreen-swapped-x-y':continue
        if path==node and token==2:body.append(struct.pack('>3I',3,0,offset))
        body.append(raw)
    body=b''.join(body);h[3]=h[2]+len(body);h[8]=len(strings);h[9]=len(body);h[1]=h[3]+h[8]
    result=struct.pack('>10I',*h)+blob[40:h[2]]+body+strings
    after=properties(result)
    expected=dict(before);del expected[node,'touchscreen-swapped-x-y'];expected[node,'touchscreen-inverted-y']=b''
    assert after==expected
    return result
