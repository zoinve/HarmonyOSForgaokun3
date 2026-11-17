"""Build a static ARM64 restricted reader; never stage keys or touch the target."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BUILD=Path('/home/zoinve/harmony-virgl-883')

if __name__ == '__main__':
    work=BUILD/'live-radio-reader-553'
    report=ROOT/'reports/live-radio-reader-553'
    assert not work.exists() and not report.exists() and not Path('/logs').exists()
    work.mkdir();report.mkdir()
    source=runpy.run_path(str(ROOT/'next-experiment/live-radio-reader-551.py'))['SOURCE']
    binary=work/'reader'
    result=subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror',
        '-x','c','-','-o',str(binary)],input=source,text=True,capture_output=True,timeout=60)
    (report/'compile.stderr').open('x').write(result.stderr)
    assert result.returncode==0,result.stderr
    data=binary.read_bytes()
    assert data[:4]==b'\x7fELF' and int.from_bytes(data[18:20],'little')==183
    tested=[]
    for command,want in [('sh',77),('radio-status; id',77),('radio-status\nstatus',77),('radio-status',74)]:
        run=subprocess.run(['qemu-aarch64',str(binary),'-c','read-only'],
            env=dict(os.environ,SSH_ORIGINAL_COMMAND=command),capture_output=True,text=True,timeout=10)
        assert run.returncode==want,(command,run.returncode,run.stderr)
        tested.append(dict(command=command,exit_status=run.returncode))
    record=dict(binary=str(binary),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                source_sha256=hashlib.sha256(source.encode()).hexdigest(),arm64_dispatch_tests=tested,
                private_keys_read=False,target_accessed=False,installed=False,
                original_authentication_unchanged=True,native_radio_observed=False)
    (report/'result.json').open('x').write(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))
