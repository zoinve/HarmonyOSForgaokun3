"""Read original codec ELF dependencies and symbols, never execute or patch."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

base=Path(__file__).resolve().parents[1]
out=base/'reports/commercial-decoder-audit-070'
out.mkdir()
image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
paths=['/system/lib64/libhevcdec_ohos.z.so','/system/lib64/libhevc_decoder.z.so',
       '/system/lib64/libfcodec.z.so','/system/lib64/libl410ffmpeg.z.so',
       '/system/lib64/chipset-sdk/libohosffmpeg.z.so']
rows=[]
for path in paths:
    data=subprocess.check_output(['debugfs','-R','cat '+path,str(image)],stderr=subprocess.DEVNULL)
    assert data[:6]==b'\x7fELF\x02\x01'
    file=out/Path(path).name
    file.open('xb').write(data)
    dynamic=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(file)]).decode()
    symbols=subprocess.check_output(['aarch64-linux-gnu-nm','-D','-C',str(file)]).decode()
    (out/(file.name+'.dynamic.txt')).open('x').write(dynamic)
    (out/(file.name+'.symbols.txt')).open('x').write(symbols)
    assembly=subprocess.check_output(['llvm-objdump-19','-d','--demangle',str(file)])
    (out/(file.name+'.disassembly.txt')).open('xb').write(assembly)
    strings=[x.decode() for x in re.findall(rb'[ -~]{6,}',data)]
    rows.append(dict(path=path,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
        dependencies=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic),
        selected_symbols=[x for x in symbols.splitlines() if any(k in x for k in ['HEVC_','avcodec_open2','avcodec_find_decoder','avcodec_send_packet','avcodec_receive_frame'])],
        selected_strings=[x for x in strings if any(k in x.lower() for k in [
            '/data/','/dev/','l410','kylin','cannot open','init failed'])]))
result=dict(original_image_written=False,original_libraries_executed=False,
    private_live_objects_read=False,library_patched=False,libraries=rows)
(out/'result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
