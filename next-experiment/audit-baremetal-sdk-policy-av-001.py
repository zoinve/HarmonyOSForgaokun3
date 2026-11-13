"""Read the unchanged production binary policy using the already installed host libsepol."""
import subprocess

payload=r'''
from pathlib import Path
import ctypes as C,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-sdk-policy-av-001.json')
assert not local.exists()
policy=root/'baremetal-selinux-load-019/policy.31';assert hashlib.sha256(policy.read_bytes()).hexdigest()=='3119d6aae760a6d692459ce9d83aeb6354301bc1fb9b084d005664f6a543d8e5'
lib=C.CDLL('libsepol.so.2');libc=C.CDLL(None)
libc.fopen.argtypes=[C.c_char_p,C.c_char_p];libc.fopen.restype=C.c_void_p
libc.fclose.argtypes=[C.c_void_p];libc.fclose.restype=C.c_int
lib.sepol_set_policydb_from_file.argtypes=[C.c_void_p];lib.sepol_set_policydb_from_file.restype=C.c_int
lib.sepol_context_to_sid.argtypes=[C.c_char_p,C.c_size_t,C.POINTER(C.c_uint32)];lib.sepol_context_to_sid.restype=C.c_int
lib.sepol_string_to_security_class.argtypes=[C.c_char_p,C.POINTER(C.c_uint16)];lib.sepol_string_to_security_class.restype=C.c_int
lib.sepol_string_to_av_perm.argtypes=[C.c_uint16,C.c_char_p,C.POINTER(C.c_uint32)];lib.sepol_string_to_av_perm.restype=C.c_int
class Decision(C.Structure):
 _fields_=[('allowed',C.c_uint32),('decided',C.c_uint32),('auditallow',C.c_uint32),('auditdeny',C.c_uint32),('seqno',C.c_uint32),('flags',C.c_uint32)]
lib.sepol_compute_av.argtypes=[C.c_uint32,C.c_uint32,C.c_uint16,C.c_uint32,C.POINTER(Decision)];lib.sepol_compute_av.restype=C.c_int
f=libc.fopen(str(policy).encode(),b'rb');assert f
try:assert lib.sepol_set_policydb_from_file(f)==0
finally:libc.fclose(f)
def context(name):return 'u:'+('r:' if name in ['init','samgr','accesstoken_service'] else 'object_r:')+name+':s0'
def query(source,target,kind,permission):
 ss=C.c_uint32();ts=C.c_uint32();cl=C.c_uint16();av=C.c_uint32();d=Decision()
 for text,dest in [(context(source),ss),(context(target),ts)]:
  b=text.encode();assert lib.sepol_context_to_sid(b,len(b)+1,C.byref(dest))==0,text
 assert lib.sepol_string_to_security_class(kind.encode(),C.byref(cl))==0,kind
 assert lib.sepol_string_to_av_perm(cl,permission.encode(),C.byref(av))==0,permission
 assert lib.sepol_compute_av(ss,ts,cl,av,C.byref(d))==0
 return dict(source=context(source),target=context(target),object_class=kind,permission=permission,allowed=bool(d.allowed&av.value),permissive_domain=bool(d.flags&1))
rows=[]
for source,target in [('init','init'),('init','samgr'),('samgr','samgr')]:
 for p in ['call','transfer','set_context_mgr']:rows.append(query(source,target,'binder',p))
for source in ['init','samgr']:
 for target in ['dev_at_file','dev_binder_file']:
  for p in ['open','read','write','ioctl']:rows.append(query(source,target,'chr_file',p))
for target in ['init_exec','samgr_exec','system_lib_file']:
 for p in ['execute','execute_no_trans','map']:rows.append(query('init',target,'file',p))
report=dict(policy_sha256=hashlib.sha256(policy.read_bytes()).hexdigest(),policy_modified=False,kernel_policy_changed=False,queries=rows,runtime_authorization_verified=False)
local.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
'''
compile(payload,'policy-av-audit-001','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60)
    raise SystemExit(r.returncode)
