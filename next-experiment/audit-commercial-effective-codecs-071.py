"""Resolve runtime-mapped original image inodes, preserving earlier audits."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

base=Path(__file__).resolve().parents[1]
out=base/'reports/commercial-effective-codecs-audit-071'
out.mkdir()
image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
paths=[
 '/system/lib64/l410-h264-decoder-v1/libfcodec.z.so',
 '/system/lib64/l410-h264-decoder-v1/libl410ffmpeg.z.so',
 '/system/lib64/l410-codec-sandbox-v1/libhevc_decoder.z.so',
 '/system/lib64/l410-codec-sandbox-v1/libhevcdec_ohos.z.so',
 '/system/bin/l410-launch-kylin-h264-decoder.sh',
 '/system/bin/l410-launch-kylin-video-decoder.sh',
 '/system/bin/l410_kylin_h264_decoder_helper',
 '/system/bin/l410_kylin_video_decoder_helper',
 '/system/lib64/l410-kylin-video-decoder-v1/libavcodec.so.58',
]
rows=[]
for path in paths:
    data=subprocess.check_output(['debugfs','-R','cat '+path,str(image)],stderr=subprocess.DEVNULL)
    assert data
    relative=path.removeprefix('/system/')
    target=out/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    target.open('xb').write(data)
    row=dict(path=path,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    if data[:4]==b'\x7fELF':
        dynamic=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(target)]).decode()
        (target.parent/(target.name+'.dynamic.txt')).open('x').write(dynamic)
        row['dependencies']=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic)
        row['selected_strings']=[x.decode() for x in re.findall(rb'[ -~]{6,}',data) if any(k in x.lower()
            for k in [b'/data/',b'/dev/',b'kylin',b'h264_omx',b'hevc_omx',b'software fallback'])]
    else:
        row['script']=data.decode()
    rows.append(row)
codec=json.loads((base/'reports/commercial61-native-071/codec-analysis.json').read_text())
assert codec['attachment_count']==0 and codec['errors']
result=dict(run=codec['run'],libraries_and_helpers=rows,
    runtime_inode_resolution=subprocess.check_output(['debugfs','-R','ncheck 265870 271005 265869',str(image)],stderr=subprocess.DEVNULL).decode(),
    original_images_written=False,libraries_executed=False,private_objects_read=False,
    original_071_register_samples=0,original_071_mapping_refusal_preserved=True,
    runtime_loader_existence_not_measured=True,desktop_verified=False)
(out/'result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
