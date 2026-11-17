"""Inspect original storage path/mount contracts without executing their ELFs."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    report=ROOT/'reports/storage-contract-181'
    assert not report.exists(), 'preserve numbered evidence'
    tools=runpy.run_path(str(BASE/'audit-board-driver-contracts-126.py'))
    resolve=runpy.run_path(str(BASE/'audit-usb-implementation-150.py'))['resolve']
    read,names=tools['read'],tools['names']
    image=tools['IMAGES']/'p111-system.kr990-ext4-v1.img'
    paths=['/system/bin/storage_daemon','/system/bin/mount.ntfs','/system/bin/fsck.ntfs',
        '/system/lib64/l410-storage-compat-v303/libstorage_no_hmdfs_param.so']
    paths += ['/system/lib64/'+name for name in names(image,'/system/lib64')
              if re.search(r'^lib(?:storage|volume)',name,re.I) and '.so' in name]
    report.mkdir()
    rows=[]
    for index,path in enumerate(paths):
        target,data,links=resolve(read,path)
        row=dict(requested=path,resolved=target,links=links,elf_present=bool(data))
        if data:
            binary=report/(str(index)+'-'+target.rsplit('/',1)[1])
            binary.open('xb').write(data)
            dynamic=subprocess.check_output(['readelf','-d',str(binary)],text=True)
            symbols=subprocess.check_output(['readelf','--dyn-syms','--wide',str(binary)],text=True)
            strings=subprocess.run(['strings','-a'],input=data,capture_output=True,check=True).stdout.decode(errors='replace').splitlines()
            selected=[line for line in strings if re.search(
                r'/devices/|/sys/(?:block|class/block|dev/block)|/dev/block|mount\.(?:ntfs|exfat)|fnmatch|coldboot|cold.boot|read.only|readOnly|ReadOnly|MS_RDONLY|public:|uevent|Uevent|UEVENT',line)]
            row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                needed=re.findall(r'\(NEEDED\).*?\[([^]]+)\]',dynamic),
                selected_strings=selected,
                metadata_symbols=[line for line in symbols.splitlines() if re.search(r'fnmatch|mknod|mount|ioctl|realpath|ReadOnly|Coldboot|ColdBoot|Uevent',line)])
        rows.append(row)
    result=dict(files=rows,source_images_opened_read_only=True,binaries_executed=False,
        binaries_modified=False,target_modified=False,native_storage_acceptance=False)
    (report/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(dict(files=[dict(path=row['requested'],elf_present=row['elf_present'],
        path_patterns=[s for s in row.get('selected_strings',[]) if s.startswith(('/devices/','/dev/block','/sys/'))]) for row in rows]),indent=2))
