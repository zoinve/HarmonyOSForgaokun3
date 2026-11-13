"""Read-only original HiLog decoder symbols; no target execution or image writes."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-loader-001.py')))['payload']
payload = payload.replace('original-parameter-loader-001', 'original-hilog-decoder-001')
payload = payload.replace("work/'init'", "work/'libhilog_inner.so'")
payload = payload.replace('/system/bin/init', '/system/lib64/libhilog_inner.so')
payload = payload.replace('original_init_elf_', 'original_hilog_elf_')
payload = payload.replace("commands=[", r'''
import lzma,struct
body=elf.read_bytes()
assert sha(elf)=='d57bd768c245f182918c4e82aae7400ab8be07f1de50c63a6733bf980655ac44'
shoff=struct.unpack_from('<Q',body,40)[0]
entsize,count,namesindex=struct.unpack_from('<HHH',body,58)
sections=[struct.unpack_from('<IIQQQQIIQQ',body,shoff+i*entsize) for i in range(count)]
names=sections[namesindex]
strings=body[names[4]:names[4]+names[5]]
debug=[s for s in sections if strings[s[0]:].split(b'\0',1)[0]==b'.gnu_debugdata']
assert len(debug)==1
section=debug[0]
mini=work/'mini.elf'
mini.write_bytes(lzma.decompress(body[section[4]:section[4]+section[5]]))
assert mini.read_bytes()[:5]==b'\x7fELF\x02'
commands=[['llvm-nm-19','-anC',str(mini)],''')
compile(payload, 'original-hilog-decoder-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
