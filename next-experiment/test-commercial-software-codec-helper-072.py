"""Native socket/shared-buffer tests, using exact original video frame hashes."""
from pathlib import Path
import base64
import json
import runpy
import subprocess
import sys

base = Path(__file__).resolve().parent
assert sys.argv[1:] in ([], ['--isolated'])
isolated = sys.argv[1:] == ['--isolated']
out = base.parent / ('reports/commercial-software-codec-helper-test-072' + ('-isolated-r2' if isolated else ''))
out.mkdir()
workflow = runpy.run_path(str(base / 'commercial-workflow-071.py'))
workflow['configure_local_transport']()
source = (base / 'commercial-software-codec-helper-072.c').read_bytes()
code = r'''
from pathlib import Path
import array,base64,hashlib,json,mmap,os,socket,struct,subprocess,time
root=Path.home()/'.local/share/harmony-arm64-kvm-lab/software-codec-build-072'
test=root/('iso-test-r2' if ISOLATED else 'socket-test');test.mkdir()
src=root/'commercial-software-codec-helper-072.c'
if ISOLATED:assert src.read_bytes()==base64.b64decode(SOURCE)
else:
 with src.open('xb') as f:f.write(base64.b64decode(SOURCE))
headers=root/'sysroot/usr/include/aarch64-linux-gnu'
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
timer=['systemctl','is-active','harmony-lab-screen-off-001.timer']
assert subprocess.check_output(timer,text=True).strip()=='active'
compile_results=[]
for name,flags in ([] if ISOLATED else [('helper',['-O2']),('helper-sanitize',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]):
 cmd=['cc','-std=c11','-Wall','-Wextra','-Werror','-pthread','-I'+str(headers),str(src),
  '-Wl,-z,relro,-z,now','-l:libavcodec.so.62','-l:libavutil.so.60','-o',str(test/name)]+flags
 run=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 compile_results.append(dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
 with (test/(name+'.compile.json')).open('x') as f:json.dump(compile_results[-1],f,indent=2)
 assert run.returncode==0,run.stderr

REQ=struct.Struct('<6IQ');RES=struct.Struct('<IIiIIIIIQIIIIi4x')
assert REQ.size==32 and RES.size==64
MAGIC=0x3144564b;IN=8*1024*1024;SLOT=16*1024*1024
def request(op,size=0,pts=0,codec=0,channel=0):
 return REQ.pack(MAGIC,1,op,channel,size,codec,pts)
def response(s):
 data=s.recv(128);assert len(data)==64,len(data)
 values=RES.unpack(data);assert values[:2]==(MAGIC,1)
 return dict(zip(['magic','version','status','consumed','width','height','stride','depth','pts','y','u','v','size','error'],values))
def transact(s,data):
 s.sendall(data);return response(s)
def start(mode,uid):
 path=str(test/(mode+'-'+str(uid)+'.sock'))
 log=(test/(mode+'-'+str(uid)+'.stdout')).open('xb')
 err=(test/(mode+'-'+str(uid)+'.stderr')).open('xb')
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:abort_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
 runtime=root/'runtime'
 command=([str(runtime/'ld-linux-aarch64.so.1'),'--library-path',str(runtime),str(runtime/'helper')] if ISOLATED else [str(test/'helper-sanitize')])
 proc=subprocess.Popen(command+[path,mode,str(uid)],stdout=log,stderr=err,env=env)
 for _ in range(100):
  if Path(path).exists():break
  assert proc.poll() is None,'helper exited during startup'
  time.sleep(.05)
 assert Path(path).exists()
 return proc,path,log,err
def connect(path):
 s=socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET);s.settimeout(10);s.connect(path);return s
def buffers(outcap):
 fds=[os.memfd_create('codec-input',os.MFD_CLOEXEC),os.memfd_create('codec-output',os.MFD_CLOEXEC)]
 os.ftruncate(fds[0],IN);os.ftruncate(fds[1],outcap)
 maps=[mmap.mmap(fds[0],IN),mmap.mmap(fds[1],outcap)]
 return fds,maps
def create(s,fds,codec):
 s.sendmsg([request(1,codec=codec)],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))])
 return response(s)
def packet_bytes(data):
 chunks=[];offset=0
 for line in data.splitlines():
  if not line:continue
  prefix,body=line.split(':',1)
  assert int(prefix,16)==offset
  chunk=bytes.fromhex(body.strip().split('  ',1)[0]);assert 0<len(chunk)<=16
  chunks.append(chunk);offset+=len(chunk)
 return b''.join(chunks)
assets=Path.home()/'.local/share/harmony-arm64-kvm-lab/codec-software-test-072'
results=[];malformed=[];helpers=[]
try:
 for mode in ['ring','legacy']:
  proc,path,log,err=start(mode,os.getuid());helpers.append((proc,path,log,err))
  # Reject truncated/oversized control packets, wrong magic, invalid FD counts,
  # undersized buffers and aliasing before allowing any decoder input.
  before=len(list(Path('/proc/'+str(proc.pid)+'/fd').iterdir()))
  for case in ['short','oversize','magic','missing-fds','extra-fd','small','alias']:
   s=connect(path);fds,maps=buffers(32*1024*1024 if mode=='legacy' else 64*1024*1024)
   try:
    data=request(1,codec=0 if mode=='legacy' else 1)
    sendfds=fds[:]
    if case=='short':data=data[:-1]
    if case=='oversize':data+=b'x'
    if case=='magic':data=b'NOPE'+data[4:]
    if case=='missing-fds':sendfds=[]
    if case=='extra-fd':sendfds+=fds[:1]
    if case=='small':os.ftruncate(fds[0],1)
    if case=='alias':sendfds=[fds[1],fds[1]]
    ancillary=[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',sendfds))] if sendfds else []
    s.sendmsg([data],ancillary)
    try:answer=s.recv(128)
    except ConnectionResetError:answer=b''
    assert not answer or (len(answer)==64 and RES.unpack(answer)[2]<0),(case,answer)
    malformed.append(dict(mode=mode,case=case,rejected=True))
   finally:
    s.close()
    for m in maps:m.close()
    for fd in fds:os.close(fd)
  time.sleep(.1)
  assert len(list(Path('/proc/'+str(proc.pid)+'/fd').iterdir()))==before,'FD leak after malformed clients'
  for source in sorted(assets.glob('*.mp4')):
   info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-show_packets','-of','json',str(source)],text=True))
   codec=info['streams'][0]['codec_name']
   if (mode=='ring') != (codec=='h264'):continue
   elementary=test/(source.name+'.'+codec)
   conversion=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(source),'-map','0:v:0','-c','copy','-bsf:v',codec+'_mp4toannexb','-f',codec,str(elementary)],capture_output=True,text=True,timeout=30)
   assert conversion.returncode==0 and not conversion.stderr,conversion.stderr
   dump=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_packets','-show_data','-of','json',str(elementary)],text=True))
   packets=dump['packets'];original=info['packets'];assert len(packets)==len(original)
   expected=[line.split(',')[-1].strip() for line in (assets/(source.name+'.framemd5')).read_text().splitlines() if line and not line.startswith('#')]
   s=connect(path);fds,maps=buffers(64*1024*1024 if mode=='ring' else 32*1024*1024)
   held=[];hashes=[];timestamps=[];backpressure=0;started=time.monotonic()
   def accept(r):
    assert r['status']>=0,r
    if r['status']!=0:return
    w,h,pitch=r['width'],r['height'],r['stride']
    assert (w,h)==(info['streams'][0]['width'],info['streams'][0]['height'])
    assert r['depth']&255==8 and not r['depth']&0x300
    slot=(r['depth']>>16)&255
    assert slot<4 and slot not in held
    start=slot*SLOT if mode=='ring' else 0
    assert r['y']==start and r['u']==start+pitch*h and r['v']==r['u']+pitch//2*((h+1)//2)
    assert r['size']==pitch*h+pitch*((h+1)//2)
    assert start+r['size']<=len(maps[1])
    digest=hashlib.md5()
    for offset,width,rows,stride in [(r['y'],w,h,pitch),(r['u'],(w+1)//2,(h+1)//2,pitch//2),(r['v'],(w+1)//2,(h+1)//2,pitch//2)]:
     for row in range(rows):digest.update(maps[1][offset+row*stride:offset+row*stride+width])
    hashes.append(digest.hexdigest());timestamps.append(r['pts'])
    assert bool(r['depth']&0x400)==(mode=='ring')
    if mode=='ring':held.append(slot)
   def release():
    for slot in held:
     r=transact(s,request(5,channel=slot));assert r['status']==1 and r['error']==0,r
    held.clear()
   try:
    created=create(s,fds,0 if mode=='legacy' else 1|0x40000000)
    assert created['status']==1 and created['error']==0,created
    for packet,orig in zip(packets,original):
     data=packet_bytes(packet['data']);assert len(data)==int(packet['size'])<=IN
     maps[0][:len(data)]=data
     pts=int(orig['pts']) & ((1<<64)-1)
     q=request(2,len(data),pts)
     if len(held)==4:
      before_bytes=hashlib.sha256(maps[1]).digest()
      r=transact(s,q)
      assert r['status']==1 and r['consumed']==0 and r['error']==-11,r
      assert hashlib.sha256(maps[1]).digest()==before_bytes,'locked slots overwritten'
      backpressure+=1;release()
     for retry in range(10):
      r=transact(s,q);accept(r)
      assert r['consumed'] in (0,len(data)),r
      if r['consumed']:break
      if len(held)==4:release()
     else:raise AssertionError('packet never consumed')
    release()
    for _ in range(len(expected)+30):
     r=transact(s,request(3));accept(r)
     release()
     if r['status']==1 and r['error']==-541478725:break
    else:raise AssertionError('no EOF')
    assert hashes==expected,(source.name,len(hashes),len(expected),next((i for i,(a,b) in enumerate(zip(hashes,expected)) if a!=b),None))
    frames=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(source)],text=True))['frames']
    assert timestamps==[int(f['pts']) & ((1<<64)-1) for f in frames],'reordered presentation timestamps differ'
    deleted=transact(s,request(4));assert deleted['status']==1
    results.append(dict(name=source.name,mode=mode,packets=len(packets),frames=len(hashes),all_frame_md5_match=True,all_presentation_timestamps_match=True,backpressure_checks=backpressure,seconds=time.monotonic()-started,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
   finally:
    s.close()
    for m in maps:m.close()
    for fd in fds:os.close(fd)
  assert proc.poll() is None
 # Exact-UID guard must reject an otherwise valid connection.
 proc,path,log,err=start('ring',os.getuid()+1);helpers.append((proc,path,log,err))
 s=connect(path)
 try:
  try:answer=s.recv(128)
  except ConnectionResetError:answer=b''
  assert not answer
 finally:s.close()
 assert len(results)==8 and sum(r['frames'] for r in results)==1980
finally:
 for proc,path,log,err in helpers:
  proc.terminate()
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)
  log.close();err.close()
  stderr=Path(err.name).read_text()
  assert 'AddressSanitizer' not in stderr and 'runtime error:' not in stderr,stderr
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
assert subprocess.check_output(timer,text=True).strip()=='active'
result=dict(boot_id=boot,workdir=str(test),compiles=compile_results,videos=results,malformed_requests=malformed,exact_peer_uid_rejection=True,all_1980_frames_match=True,asan_ubsan_no_report=not ISOLATED,isolated_runtime_decode_verified=ISOLATED,helper_sha256=hashlib.sha256(((root/'runtime/helper') if ISOLATED else (test/'helper')).read_bytes()).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),harmonyos_backend_integrated=False,desktop_verified=False,interaction_verified=False)
with (test/'result.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''
run = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
    '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
    '-o', 'ConnectTimeout=10', 'matebook', 'python3 -'],
    input='ISOLATED=' + repr(isolated) + '\nSOURCE=' + repr(base64.b64encode(source).decode()) + '\n' + code,
    text=True, capture_output=True, timeout=1200)
(out / 'ssh.stdout').open('x').write(run.stdout)
(out / 'ssh.stderr').open('x').write(run.stderr)
assert run.returncode == 0, run.stderr
result = json.loads(run.stdout)
(out / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
