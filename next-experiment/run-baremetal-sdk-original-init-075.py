"""Same verified ashmem-enabled guest; additionally capture virtual scanout via QMP."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-074.py')))['payload']
for old, new in [('original-init-qemu-074', 'original-init-qemu-075'),
                 ('harmony-sdk-qemu074-', 'harmony-sdk-qemu075-')]:
    assert old in payload, old
    payload = payload.replace(old, new)
anchor = "report=dict(bounded_observation_complete=False"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """qmp_socket=work/'qmp.sock'
command+=['-qmp','unix:'+str(qmp_socket)+',server=on,wait=off']
# Helper permits only qmp_capabilities, query-status and screendump.
import runpy
capture_frame=runpy.run_path(str(local.parent.parent/'next-experiment/original-graphics-qmp-capture-001.py'))['capture_frame']
""" + anchor)
old = """  try:
   r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=360)
   report['qemu_returncode']=r.returncode;report['observation_timed_out']=False
  except subprocess.TimeoutExpired:
   report['qemu_returncode']=None;report['observation_timed_out']=True"""
assert payload.count(old) == 1
payload = payload.replace(old, """  process=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT)
  captures=[]
  try:
   for target in (120,240,330,360):
    try:
     code=process.wait(timeout=max(0.01,target-(time.monotonic()-start)))
     report['qemu_returncode']=code;report['observation_timed_out']=False
     break
    except subprocess.TimeoutExpired:
     if target==360:
      process.kill();process.wait(timeout=15)
      report['qemu_returncode']=None;report['observation_timed_out']=True
      break
     try:
      frame=capture_frame(qmp_socket,work/('frame-'+str(target)+'.ppm'))
      frame['elapsed_seconds']=time.monotonic()-start
      for artifact in frame['files']:
       original=Path(artifact['path']);destination=local/original.name
       with destination.open('xb') as output:output.write(original.read_bytes())
       assert sha(destination)==artifact['sha256']
      captures.append(frame)
     except Exception as error:
      captures.append(dict(target_seconds=target,error=type(error).__name__+': '+str(error),guest_pixels_observed=False))
  finally:
   if process.poll() is None:
    process.kill();process.wait(timeout=15)
   report['virtual_scanout_captures']=captures""")
compile(payload, 'original-virtual-scanout-075', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)
