"""Read-only 031 input/display evidence audit; this does not implement a repair."""
from pathlib import Path
import hashlib, json, struct, subprocess

base = Path(__file__).resolve().parent.parent
evidence = base / 'reports/native-touchpad-statusbar-032'
raw = evidence / 'raw'
log = (raw / 'interactive-hilog030.log').read_text(errors='replace')
expected = {
    'interactive-hilog030.log': 'de66666b4fd6f98b2f94a6794139dd1dde2fab913e961470537bfd03cbd28f55',
    'interactive-faults030.log': '55788f44b86b55943e38a61d06618ec7f0ec03fa2e82a0a23c9a476e80c98a31',
}
for name, digest in expected.items():
    data = (raw / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, name
    assert b'\0' not in data, name
for text in ['Touchpad', 'tp_new_touch', 'P:M:1335', 'width: 2560, height: 1600, landscape: false']:
    assert text in log, text

payload = r'''
from pathlib import Path
import hashlib,json,struct,subprocess
r=Path('/home/zoinve/harmony-virgl-883/native-touchpad-statusbar-032')
p=r/'libcursor_drawing_adapter.z.so';b=p.read_bytes()
assert b[:6]==b'\x7fELF\x02\x01'
def at(va,fmt):
 phoff=struct.unpack_from('<Q',b,32)[0]
 entsize,count=struct.unpack_from('<HH',b,54)
 for i in range(count):
  typ,flags,off,addr,phys,filesz,memsz,align=struct.unpack_from('<IIQQQQQQ',b,phoff+i*entsize)
  if typ==1 and addr<=va and va+struct.calcsize(fmt)<=addr+filesz:
   return struct.unpack_from(fmt,b,off+va-addr)[0]
 raise AssertionError(('unmapped VA',hex(va)))
assert at(0xbe84,'<I')==0xd65f03c0 # bare AArch64 RET
assert at(0x19ea8+2*8,'<Q')==0xbe84
assert at(0x19ea8+14*8,'<Q')==0xbe84
assert at(0x19ea8+23*8,'<Q')==0xdac4
assert [at(0xdac4+i*4,'<I') for i in range(3)]==[0x2a1f03e0,0xf900003f,0xd65f03c0]
sections=[]
for name,start,end in [('libcursor_drawing_adapter.z.so',0xbe84,0xbe88),
                       ('libcursor_drawing_adapter.z.so',0xdac4,0xdad0),
                       ('libmmi-server.z.so',0x28f340,0x28f3ac),
                       ('libmmi-server.z.so',0x28fd98,0x28fdcc)]:
 sections.append(subprocess.check_output(['aarch64-linux-gnu-objdump','-d','-C',
   '--start-address='+hex(start),'--stop-address='+hex(end),str(r/name)],text=True))
print(json.dumps(dict(adapter_sha256=hashlib.sha256(b).hexdigest(),
 draw_pointer_slot=2,set_location_slot=14,both_are_bare_return=True,
 get_cursor_surface_id_returns_zero=True,disassembly='\n'.join(sections))))
'''
run = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                     input=payload, text=True, capture_output=True, timeout=30)
assert run.returncode == 0, run.stderr
result = json.loads(run.stdout)
disassembly = result.pop('disassembly')
out = evidence / 'cursor-abi-audit-032.txt'
if not out.exists():
    out.write_text(disassembly, encoding='utf-8')
else:
    assert out.read_text(encoding='utf-8') == disassembly
result.update(log_hashes=expected, physical_motion_reaches_settings=True,
              display_dimensions=[2560, 1600],
              statusbar_root_cause_confirmed=False, click_path_verified=False,
              remote_hash_comparison_completed=False, repair_implemented=False,
              candidate_installed=False)
print(json.dumps(result, indent=2))
