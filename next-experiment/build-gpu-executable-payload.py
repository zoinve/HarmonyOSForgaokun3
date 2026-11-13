"""Fresh 889: retain 888 binaries, correct standalone probe archive mode only."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-889'
assert not out.exists()
out.mkdir()
original = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(', 1)[1].split("'''", 1)[0]
setup = r'''
from pathlib import Path
import shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'executable-probe-889';work.mkdir()
ram=work/'ramroot'
shutil.copytree(root/'dispatch-probe-888/ramroot',ram,symlinks=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-889')
'''
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
               input=setup + archive, text=True, check=True)
