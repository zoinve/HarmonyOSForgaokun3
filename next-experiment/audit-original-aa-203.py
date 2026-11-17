'''Read the original commercial CLI help strings without running or changing it.'''
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parent.parent
IMAGE=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


if __name__=='__main__':
    report=ROOT/'reports/original-aa-203';assert not report.exists()
    with IMAGE.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    assert digest=='b31050d8d8887b15736d88a379079defa206780d80b8310acca88abf7acff0df'
    proc=subprocess.run(['debugfs','-R','cat /bin/aa',str(IMAGE)],capture_output=True,timeout=120)
    assert proc.returncode==0 and proc.stdout.startswith(b'\x7fELF'),proc.stderr.decode(errors='replace')
    selected=[]
    for value in re.findall(rb'[\x20-\x7e\t\r\n]{6,}',proc.stdout):
        lower=value.lower()
        if (b'usage: aa start' in lower or b'--user' in lower or b'userid' in lower or b'user id' in lower):
            assert len(value)<=32768
            selected.append(value.decode('ascii'))
    result=dict(original_system_image_sha256=digest,original_aa_sha256=hashlib.sha256(proc.stdout).hexdigest(),
        selected_original_strings=selected,original_cli_executed=False,original_cli_modified=False,
        target_modified=False,raw_tokens_exported=False)
    report.mkdir()
    (report/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
