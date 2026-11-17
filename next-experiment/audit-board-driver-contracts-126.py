"""Locate original HDI/VDI and display-power paths in immutable source images."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
IMAGES=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092')

def read(image,command,optional=False):
    r=subprocess.run(['debugfs','-R',command,str(image)],capture_output=True,check=True)
    if b'File not found' in r.stderr:
        assert optional,(command,r.stderr)
        return b''
    return r.stdout

def names(image,directory):
    return [line.split('/')[5] for line in read(image,'ls -p '+directory,True).decode().splitlines()
            if line.startswith('/') and len(line.split('/'))>5 and line.split('/')[5] not in ['.','..']]

if __name__=='__main__':
    folder=ROOT/'reports/board-driver-contracts-126'
    assert not folder.exists()
    folder.mkdir()
    rows=[];configs=[];inventories={}
    selected=re.compile(r'^libdm\.|battery|display.*power|display.*manager|backlight|brightness|light_interface|display_interface|display_composer',re.I)
    for image_name,prefix in [('p111-system.kr990-ext4-v1.img','/system'),('p109-vendor.kr990-ext4-v1.img','/vendor')]:
        image=IMAGES/image_name
        for directory in [prefix+'/lib64',prefix+'/lib64/hw',prefix+'/lib64/chipset-sdk',prefix+'/etc/init',prefix+'/etc/hdfconfig',prefix+'/etc/battery',prefix+'/etc/power_config']:
            entries=names(image,directory)
            inventories[directory]=entries
            for name in entries:
                path=directory+'/'+name
                if '/lib64' in directory and selected.search(name):
                    data=read(image,'cat '+path)
                    if not data.startswith(b'\x7fELF'):continue
                    target=folder/(prefix.strip('/')+'-'+name)
                    target.open('xb').write(data)
                    symbols=subprocess.check_output(['readelf','--dyn-syms','--wide',str(target)],text=True)
                    dynamic=subprocess.check_output(['readelf','-d',str(target)],text=True)
                    text=subprocess.run(['strings','-a'],input=data,capture_output=True,check=True).stdout.decode(errors='replace').splitlines()
                    rows.append(dict(path=path,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),dynamic=dynamic,
                        relevant_symbols=[line for line in symbols.splitlines() if re.search(r'Brightness|Backlight|Battery|Capacity|Temperature|Voltage|Current|Hdf|Hdi|DriverEntry',line)],
                        selected_strings=[line for line in text if re.search(r'/sys/|/dev/|battery|backlight|brightness|l410|gaokun',line,re.I)][:250]))
                elif '/etc/' in directory and re.search(r'battery|power|display|light|hdf',name,re.I):
                    data=read(image,'cat '+path)
                    try:content=json.loads(data)
                    except (ValueError,UnicodeError):continue
                    configs.append(dict(path=path,sha256=hashlib.sha256(data).hexdigest(),content=content))
    result=dict(inventories=inventories,libraries=rows,configs=configs,source_images_read_only=True,
        image_written=False,binaries_patched=False,binaries_executed=False)
    (folder/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(dict(libraries=[r['path'] for r in rows],configs=[r['path'] for r in configs]),indent=2))
