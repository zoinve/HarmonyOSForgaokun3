"""Inspect image ALSA launch/IPC contracts without enabling its services."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p109-vendor.kr990-ext4-v1.img')


if __name__ == '__main__':
    report = ROOT / 'reports/audio-helper-143'
    assert not report.exists()
    tools = runpy.run_path(str(ROOT / 'next-experiment/audit-board-driver-contracts-126.py'))
    read, names = tools['read'], tools['names']
    paths = [directory + '/' + name for directory in ['/bin', '/lib64'] for name in names(IMAGE, directory)
             if any(part in name.lower() for part in ['alsa', 'asound', 'audio_primary'])]
    report.mkdir()
    rows = []
    for path in paths:
        data = read(IMAGE, 'cat ' + path, True)
        if not data:
            continue
        target = report / Path(path).name
        target.open('xb').write(data)
        row = dict(path='/vendor' + path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), elf=data.startswith(b'\x7fELF'))
        if row['elf']:
            row['elf_headers'] = subprocess.check_output(['readelf', '-h', '-l', '-d', str(target)], text=True)
            text = subprocess.run(['strings', '-a'], input=data, capture_output=True, check=True).stdout.decode(errors='replace').splitlines()
            row['backend_contract_strings'] = [line for line in text if any(part in line for part in
                ['libasound', 'snd_pcm_', '/dev/', '/data/', 'hw:', 'default', '/lib/', 'L410_', 'LD_LIBRARY'])]
        else:
            row['text'] = data.decode('utf-8')
        rows.append(row)
    result = dict(original_vendor_image_opened_read_only=True, target_state_modified=False,
                  helpers_executed=False, original_elf_patched=False, files=rows)
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps([dict(path=r['path'], bytes=r['bytes'], elf=r['elf']) for r in rows], indent=2))
