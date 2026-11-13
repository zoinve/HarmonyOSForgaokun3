"""Fresh 886: retain 885 diagnostics, include the real GBM backend module."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-886'
assert not out.exists()
source = runpy.run_path(str(base / 'gbm-probe.py'))['gbm_probe']((base / 'payload-885/init.c').read_text())
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-886'
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
out.mkdir()
(out / 'init.c').write_text(source)
subprocess.run(['scp', str(out / 'init.c'), str(base / 'bounded-shell.c'), 'matebook:' + remote + '/'], check=True)
subprocess.run(['ssh', 'matebook', f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'], check=True)
subprocess.run(['scp', 'matebook:' + remote + '/init', str(out / 'init')], check=True)
original = (base / 'build-gpu-frontend-payload.py').read_text()
script = original.split("script = r'''", 1)[1].split("'''", 1)[0]
script = script.replace("next-experiment/payload-885", "next-experiment/payload-886")
script = script.replace("ram=root/'frontend-probe-885/ramroot';shutil.copytree(root/'system-overlay-883/ramroot',ram,symlinks=True)",
    "ram=root/'gbm-probe-886/ramroot';shutil.copytree(root/'frontend-probe-885/ramroot',ram,symlinks=True)\nshutil.copytree(root/'prefix/system/lib64/lab-virgl883/gbm',ram/'gpu883-libs/gbm',symlinks=True)")
script = script.replace("shutil.copy2(root/'frontend-probe-885/gpu-frontend-probe',ram/'gpu883-libs/gpu-frontend-probe')", "assert (ram/'gpu883-libs/gbm/dri_gbm.so').is_file()")
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script, text=True, check=True)
