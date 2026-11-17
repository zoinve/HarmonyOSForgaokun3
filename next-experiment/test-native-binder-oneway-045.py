"""Compile the exact changed branch, and constrain the kernel source delta."""
from pathlib import Path
import runpy
import subprocess
import tempfile

b = Path(__file__).resolve().parent
patch = runpy.run_path(str(b / 'native-binder-oneway-045.py'))
old = (b.parent / 'reports/native-binder-kernel-031/binder.c').read_text()
new = patch['repair'](old)
assert new.replace(patch['NEW'], patch['OLD'], 1) == old
assert new.count('put_pid(t->sender_pid_ref);') == old.count('put_pid(t->sender_pid_ref);')
branch = patch['NEW'].split('} else {', 1)[1].split('\n\t\t}\n\n\t\tret =', 1)[0]
source = r'''
#include <assert.h>
#define BR_TRANSACTION 1
#define BR_TRANSACTION_SEC_CTX 2
#define BR_REPLY 3
#define TF_ONE_WAY 1
struct tx { unsigned flags; int *sender_pid_ref; };
struct result { int sender_pid; };
#ifdef CONFIG_ACCESS_TOKENID
static int current;
static int task_active_pid_ns(int c) { return c; }
static int pid_nr_ns(int *pid,int ns) { assert(ns==current);return *pid; }
#endif
static int delivery(int cmd,unsigned flags,int real)
{
    struct tx value={flags,&real},*t=&value;
    struct result output={-1},*trd=&output;
    (void)t;(void)cmd;
''' + branch + r'''
    return output.sender_pid;
}
int main(void)
{
#ifdef CONFIG_ACCESS_TOKENID
    assert(delivery(BR_TRANSACTION,TF_ONE_WAY,3626)==3626);
    assert(delivery(BR_TRANSACTION_SEC_CTX,TF_ONE_WAY,3626)==3626);
    assert(delivery(BR_TRANSACTION,TF_ONE_WAY,0)==0);
#else
    assert(delivery(BR_TRANSACTION,TF_ONE_WAY,3626)==0);
#endif
    assert(delivery(BR_REPLY,TF_ONE_WAY,3626)==0);
    assert(delivery(BR_REPLY,0,3626)==0);
    assert(delivery(BR_TRANSACTION,0,3626)==0);
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='binder-oneway045-') as directory:
    root = Path(directory)
    (root / 'test.c').write_text(source)
    for enabled in [True, False]:
        binary = root / str(enabled)
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined'] +
                       (['-DCONFIG_ACCESS_TOKENID'] if enabled else []) +
                       [str(root / 'test.c'), '-o', str(binary)], check=True, timeout=30)
        subprocess.run([str(binary)], check=True, timeout=10)
print('PASS: exact one-branch delta, authentic namespace PID, reply/non-OHOS unchanged, pid references retained')
