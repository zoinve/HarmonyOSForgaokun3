"""Source/lifetime regression; actual Binder and app runtime remain separate gates."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
patch=base/'native-binder-pid-031.py'
assert patch.is_file(), 'missing namespace-safe Binder PID repair'
payload='''
from pathlib import Path
import runpy
p=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-binder-pid-031.py')
r=Path('/home/zoinve/harmony-virgl-883/baremetal-identity-profile-003/linux/drivers/android')
c=(r/'binder.c').read_text();h=(r/'binder_internal.h').read_text()
assert 'thread->sender_pid_nr = t->from_pid;' in c
new,header=p['repair'](c,h)
assert 'thread->sender_pid_nr = t->from_pid;' not in new
assert 'pid_nr_ns(t->sender_pid_ref, task_active_pid_ns(current))' in new
assert 't->sender_pid_ref = get_task_pid(current, PIDTYPE_TGID);' in new
assert new.count('put_pid(t->sender_pid_ref);')==new.count('kfree(t);')==2
assert 'struct pid *sender_pid_ref;' in header
assert 'task_tgid_nr_ns(sender,' in new  # standard synchronous ABI retained
assert 'thread->tokens.sender_tokenid = t->sender_tokenid;' in new
assert 'thread->tokens.first_tokenid = t->first_tokenid;' in new
assert 'sender.sender_pid_nr = thread->sender_pid_nr;' in new
try:p['repair'](new,header)
except AssertionError:pass
else:raise AssertionError('duplicate patch accepted')
print('PASS: captured real PID reference, receiver namespace, async safe, both release paths, token/standard ABI retained')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
