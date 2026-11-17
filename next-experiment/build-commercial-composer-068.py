"""Build full-frame evidence with exactly the retained original ABI/closure."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-composer-030.py')))['payload']
payload = payload.replace('commercial-composer-030', 'commercial-composer-068').replace(
    "old=root/'commercial-graphics-014/composer-trace.cpp'",
    "old=root/'commercial-composer-030/composer-evidence-030.cpp'")
payload = payload.replace('commercial-frame-evidence-030.py', 'commercial-full-frame-068.py').replace(
    'composer-evidence-030.cpp\';new_source', 'composer-evidence-068.cpp\';new_source')
# Keep command replacement anchored to the original command's input filename.
payload = payload.replace("command[command.index(str(old))]=str(new_source)",
    "command[command.index(str(old))]=str(new_source)")
payload = payload.replace('assert command.count(str(old))==1',
    "command=[str(old) if x==str(root/'commercial-graphics-014/composer-trace.cpp') else x for x in command];assert command.count(str(old))==1")
payload = payload.replace("new_source=work/'composer-evidence-030.cpp'", "new_source=work/'composer-evidence-068.cpp'")
payload = payload.replace("'composer-evidence-030.cpp','link.stdout'", "'composer-evidence-068.cpp','link.stdout'")
payload = payload.replace('diagnostic_only=True,max_captures=128',
    "full_capture_header_sha256=sha(base/'next-experiment/native-full-capture-068.h'),full_capture_limit=1,full_capture_interval_seconds=[120,145],diagnostic_only=True,max_captures=128")
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],
        input=payload,text=True,timeout=180).returncode)
