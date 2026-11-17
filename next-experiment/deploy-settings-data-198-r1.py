'''Stream directly into the isolated LAB candidate; avoid Ubuntu-root duplication.'''
from pathlib import Path
import json
import runpy
import shlex
import subprocess

BASE = Path(__file__).resolve().parent
PREVIOUS = runpy.run_path(str(BASE / 'deploy-settings-data-198.py'))
REPORT = BASE.parent / 'reports/settings-data-deploy-198-r1'


def payload():
    code = PREVIOUS['DEPLOY']
    replacements = [
        ('import hashlib,json,os,shutil,stat,subprocess', 'import gzip,hashlib,json,os,shutil,stat,subprocess,sys'),
        ("source=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/settings-data-transfer-198/data.ext4')\n", ''),
        ('assert source.stat().st_size==8589934592 and not source.is_symlink() and sha(source)==expected\n', ''),
        ("with source.open('rb') as src,data.open('xb') as out:",
         "with gzip.GzipFile(fileobj=sys.stdin.buffer) as src,data.open('xb') as out:"),
        ('shutil.copyfileobj(src,out,1024**2);out.flush();os.fsync(out.fileno())',
         'total=0\n  while chunk:=src.read(1024**2):\n   total+=len(chunk);assert total<=8589934592\n   out.write(chunk)\n  assert total==8589934592\n  out.flush();os.fsync(out.fileno())'),
    ]
    for old,new in replacements:
        assert code.count(old)==1, old
        code=code.replace(old,new,1)
    return 'expected='+repr(PREVIOUS['HASH'])+'\n'+code


def main(report=REPORT):
    assert not report.exists(), 'preserve numbered attempt'
    code=payload();compile(code,'deploy198-r1-remote','exec')
    report.mkdir()
    with (report/'compress.stderr').open('wb') as errors:
        compressor=subprocess.Popen(['wsl','-d','Debian','-u','root','--','gzip','-1','-c',
            '/home/zoinve/harmony-virgl-883/settings-data-candidate-191-r2/data.ext4'],
            stdout=subprocess.PIPE,stderr=errors)
        try:
            result=subprocess.run(PREVIOUS['SSH']+['sudo -n python3 -c '+shlex.quote(code)],
                stdin=compressor.stdout,capture_output=True,timeout=1800)
        finally:
            compressor.stdout.close()
            if compressor.poll() is None:compressor.terminate()
            compressor.wait(timeout=30)
    for suffix,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        (report/('deploy.'+suffix)).open('xb').write(data)
    assert result.returncode==0 and compressor.returncode==0,result.stderr.decode(errors='replace')
    data=json.loads(result.stdout)
    (report/'provision.json').open('x').write(json.dumps(data,indent=2))
    print(result.stdout.decode())


if __name__=='__main__':
    main()
