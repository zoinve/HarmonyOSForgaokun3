"""Retain real BLE scanning and test acknowledged nonzero audio through OHAudio."""
from pathlib import Path
import json
import os
import re
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
BT=runpy.run_path(str(BASE/'build-bluetooth-native-341.py'))
AUDIO=BT['AUDIO'];ONCE=AUDIO['ONCE']

def outer353(source,old_digest,digest):
 source=AUDIO['outer321'](source,old_digest,digest)
 source=source.replace('/commercial61-native-321/bootstrap-runtime087','/commercial61-native-353/bootstrap-runtime087')
 launcher=runpy.run_path(str(BASE/'audio-renderer-launcher-351.py'))['launcher351']()
 source=ONCE(source,'static void native_original(void)\n{',launcher+'\nstatic void native_original(void)\n{')
 return ONCE(source,'                if(i==4||i==7)audio321_observe(child);',
   '                if(i==4||i==7)audio321_observe(child);\n                if(i==7)audio351_start(child);')

def extra353(compile_program,stage,entries):
 BT['extra341'](compile_program,stage,entries)
 compiler=str(AUDIO['BUILD']/'window-bridge/toolchain/ohos-cc')
 renderer=stage/'audio-renderer350'
 subprocess.run([compiler,'-O2','-Wall','-Wextra','-Werror',str(BASE/'native-audio-renderer-350.c'),
   '-lohaudio','-lm','-o',str(renderer)],check=True)
 imports=subprocess.check_output(['readelf','--dyn-syms','--wide',str(renderer)],text=True)
 required=sorted(set(re.findall(r'\bUND\s+(OH_Audio\w+)',imports)))
 assert required
 image=runpy.run_path(str(BASE/'build-radio-native-261.py'))['image_read'](
   'p111-system.kr990-ext4-v1.img','/system/lib64/ndk/libohaudio.so')
 assert image.startswith(b'\x7fELF')
 fd=os.memfd_create('original-ohaudio-symbols',os.MFD_CLOEXEC)
 try:
  with os.fdopen(os.dup(fd),'wb') as stream:stream.write(image)
  symbols=subprocess.check_output(['readelf','--dyn-syms','--wide','/proc/self/fd/'+str(fd)],
    text=True,pass_fds=(fd,))
 finally:os.close(fd)
 defined=set()
 for line in symbols.splitlines():
  parts=line.split()
  if len(parts)>=8 and parts[0].endswith(':') and parts[6]!='UND':
   defined.add(parts[7].split('@')[0])
 missing=sorted(set(required)-defined)
 assert not missing,missing
 (stage/'audio-renderer-abi.json').open('x').write(json.dumps(dict(
   required_original_symbols=required,missing_symbols=missing,
   source_image_read_only=True,public_api_only=True,permission_checks_unchanged=True),indent=2))
 entries['native-target/audio350']=(0o40755,b'')
 entries['native-target/audio350/renderer']=(0o100755,renderer.read_bytes())

if __name__=='__main__':
 runpy.run_path(str(BASE/'driver-builder-305.py'))['build'](
   353,AUDIO['runtime321'],outer353,AUDIO['RADIO']['vendor297'],extra353)
