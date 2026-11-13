from pathlib import Path
import runpy,struct
p=Path(__file__).with_name('native-touch-dtb-026.py')
assert p.exists(),'missing target-only touchscreen orientation patch'
m=runpy.run_path(str(p));u=lambda *v:struct.pack('>'+str(len(v))+'I',*v)
strings=b'compatible\0touchscreen-size-x\0touchscreen-size-y\0touchscreen-swapped-x-y\0touchscreen-inverted-x\0'
def name(n):
    b=n.encode()+b'\0';return b+b'\0'*((-len(b))%4)
def prop(n,b):return u(3,len(b),strings.index(n.encode()+b'\0'))+b+b'\0'*((-len(b))%4)
s=u(1)+name('')+u(1)+name('touchscreen@0')
s+=prop('compatible',b'himax,hx83121a-ts\0')+prop('touchscreen-size-x',u(2560))+prop('touchscreen-size-y',u(1600))
s+=prop('touchscreen-swapped-x-y',b'')+prop('touchscreen-inverted-x',b'')+u(2,2,9)
reserve=b'\0'*16;header=u(0xd00dfeed,56+len(s)+len(strings),56,56+len(s),40,17,16,0,len(strings),len(s))
original=header+reserve+s+strings
changed=m['landscape_dtb'](original)
before=m['properties'](original);after=m['properties'](changed)
removed=set(before)-set(after);added=set(after)-set(before)
assert removed=={('/touchscreen@0','touchscreen-swapped-x-y')}
assert added=={('/touchscreen@0','touchscreen-inverted-y')}
assert all(before[k]==after[k] for k in set(before)&set(after))
assert original[40:56]==changed[40:56]
for rx,ry in [(0,0),(2559,0),(0,1599),(2559,1599),(1000,500)]:
    physical=(ry,2559-rx)
    expected=(physical[1],1599-physical[0])
    actual=(2559-rx,1599-ry)
    assert actual==expected
try:m['landscape_dtb'](changed)
except AssertionError:pass
else:raise AssertionError('already adapted DT must be refused')
print('PASS: exact two-property delta, preserved other DT properties, physical/logical coordinate equivalence')
