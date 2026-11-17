"""Read-only image audit of original display/battery contracts and services."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
IMAGE=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')

def debug(command):
    result=subprocess.run(['debugfs','-R',command,str(IMAGE)],capture_output=True,check=True)
    assert b'File not found' not in result.stderr,(command,result.stderr)
    return result.stdout

def names(directory):
    return [line.split('/')[5] for line in debug('ls -p '+directory).decode().splitlines()
            if line.startswith('/') and len(line.split('/'))>5 and line.split('/')[5] not in ['.','..']]

if __name__=='__main__':
    folder=ROOT/'reports/basic-driver-abi-125'
    assert not folder.exists()
    folder.mkdir()
    library_names=[name for name in names('/system/lib64') if re.search(r'display.*manager|battery|xpower|backlight',name,re.I)]
    config_names=[name for name in names('/system/etc/init') if re.search(r'display|battery|power',name,re.I)]
    libraries=[]
    for name in sorted(library_names):
        data=debug('cat /system/lib64/'+name)
        if not data.startswith(b'\x7fELF'):continue
        target=folder/name
        target.open('xb').write(data)
        symbols=subprocess.check_output(['readelf','--dyn-syms','--wide',str(target)],text=True)
        dynamic=subprocess.check_output(['readelf','-d',str(target)],text=True)
        strings=subprocess.run(['strings','-a'],input=data,capture_output=True,check=True).stdout.decode(errors='replace').splitlines()
        selected=[line for line in strings if re.search(r'/sys/|/dev/|backlight|SetScreenBrightness|GetScreenBrightness|BatteryCapacity|BatteryTemperature|GetCapacity|GetVoltage|GetCurrent|power_supply',line,re.I)]
        libraries.append(dict(path='/system/lib64/'+name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),dynamic_section=dynamic,
            relevant_symbols=[line for line in symbols.splitlines() if re.search(r'Brightness|Battery|Capacity|Temperature|Voltage|Current|XPower',line)],selected_strings=selected[:300]))
    configs=[]
    for name in sorted(config_names):
        data=debug('cat /system/etc/init/'+name)
        try:content=json.loads(data)
        except (ValueError,UnicodeError):continue
        configs.append(dict(path='/system/etc/init/'+name,sha256=hashlib.sha256(data).hexdigest(),content=content))
    result=dict(source_image=str(IMAGE),libraries=libraries,configs=configs,read_only_debugfs=True,
        original_image_written=False,private_binaries_executed=False,private_binaries_patched=False,
        original_abi_not_assumed_from_reference=True)
    (folder/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(dict(libraries=[row['path'] for row in libraries],configs=[row['path'] for row in configs]),indent=2))
