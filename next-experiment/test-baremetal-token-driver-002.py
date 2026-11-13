"""Execute actual driver handlers with host substitutes for kernel primitives, not an ioctl model."""
from pathlib import Path
import runpy
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REFERENCE = Path(r'C:\Users\39255\AppData\Local\Temp\opencode\HarmonyMac-reference-816\ports\kernel\accesstokenid')
driver = (REFERENCE / 'access_tokenid.c').read_text()
if '--candidate' in sys.argv:
    driver = runpy.run_path(str(BASE / 'baremetal-token-driver-002.py'))['build_driver'](driver)
driver = '\n'.join(line for line in driver.splitlines() if not line.startswith('#include'))
header = (REFERENCE / 'access_tokenid.h').read_text()
header = '\n'.join(line for line in header.splitlines() if not line.startswith('#include'))
shim = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
#include <sys/ioctl.h>
#define __user
#define pr_err(...) ((void)0)
#define pr_info(...) ((void)0)
#define DEFINE_RWLOCK(x) int x
#define read_lock(x) ((void)(x))
#define read_unlock(x) ((void)(x))
#define write_lock(x) ((void)(x))
#define write_unlock(x) ((void)(x))
typedef unsigned int kuid_t;
typedef unsigned int kgid_t;
#define KUIDT_INIT(x) (x)
#define GLOBAL_ROOT_UID 0
#define uid_eq(a,b) ((a)==(b))
#define gid_eq(a,b) ((a)==(b))
#define GFP_KERNEL 0
#define SLAB_HWCACHE_ALIGN 0
#define THIS_MODULE NULL
#define MISC_DYNAMIC_MINOR 0
#define module_init(x)
#define module_exit(x)
#define READ_ONCE(x) (x)
#define WRITE_ONCE(x,v) ((x)=(v))
struct inode { kuid_t i_uid; kgid_t i_gid; };
struct file { struct inode *f_inode; };
struct group_info { int ngroups; kgid_t gid[8]; };
struct task { uint64_t token, ftoken; } task;
#define current (&task)
static kuid_t uid;
static struct group_info groups;
static kuid_t current_uid(void) { return uid; }
static struct group_info *get_current_groups(void) { return &groups; }
static void put_group_info(struct group_info *g) { assert(g==&groups); }
static bool fail_copy, fail_cache;
static size_t copy_to_user(void *d,const void *s,size_t n) { if(fail_copy)return n;memcpy(d,s,n);return 0; }
#define copy_from_user copy_to_user
struct kmem_cache { size_t size; };
static unsigned allocations, registrations;
static int register_error;
static struct kmem_cache *kmem_cache_create(const char *n,size_t s,size_t a,int f,void *c) {
 (void)n;(void)a;(void)f;(void)c;if(fail_cache)return NULL;
 struct kmem_cache *p=malloc(sizeof(*p));assert(p);p->size=s;return p;
}
static void *kmem_cache_zalloc(struct kmem_cache *p,int flags) { (void)flags;assert(p);void *n=calloc(1,p->size);assert(n);allocations++;return n; }
static void kmem_cache_free(struct kmem_cache *p,void *n) { assert(p&&n&&allocations);allocations--;free(n); }
static void kmem_cache_destroy(struct kmem_cache *p) { assert(p);assert(allocations==0);free(p); }
struct file_operations { void *owner; long (*unlocked_ioctl)(struct file *,unsigned int,unsigned long); long (*compat_ioctl)(struct file *,unsigned int,unsigned long); };
struct miscdevice { int minor; const char *name; const struct file_operations *fops; };
static int misc_register(struct miscdevice *m) { (void)m;if(register_error)return register_error;registrations++;return 0; }
static void misc_deregister(struct miscdevice *m) { (void)m;assert(registrations);registrations--; }
'''
tests = r'''
static long call(struct file *file,unsigned n,void *p) { return access_tokenid_ioctl(file,_IOC(_IOC_READ|_IOC_WRITE,'A',n,8),(unsigned long)p); }
int main(int argc,char **argv) {
 assert(argc==2);
 struct inode inode={3020,77};struct file file={&inode};uint64_t token=0x123456789abcdef0ULL,got=0;
 if(!strcmp(argv[1],"unsupported")) {
  assert(call(&file,0,&got)==-EOPNOTSUPP);
  assert(call(&file,9,&got)==-EOPNOTSUPP);
  for(unsigned n=16;n<=25;n++)assert(call(&file,n,&got)==-EOPNOTSUPP);
  assert(call(&file,1,NULL)==-EINVAL);
  assert(access_tokenid_ioctl(&file,_IO('T',1),(unsigned long)&got)==-EINVAL);
 } else if(!strcmp(argv[1],"identity")) {
  uid=1001;task.token=11;assert(call(&file,2,&token)==-EPERM&&task.token==11);
  uid=3081;token=0x1234;assert(call(&file,2,&token)==-EPERM);token|=1ULL<<25;assert(call(&file,2,&token)==0&&task.token==token);
  uid=0;token=0xf123456789abcdefULL;assert(call(&file,2,&token)==0);assert(call(&file,1,&got)==0&&got==token);
  uid=3020;assert(call(&file,2,&token)==0);
  uid=1001;task.ftoken=42;assert(call(&file,3,&got)==-EPERM);assert(call(&file,4,&token)==-EPERM&&task.ftoken==42);
  groups.ngroups=2;groups.gid[0]=12;groups.gid[1]=77;assert(call(&file,4,&token)==0);assert(call(&file,3,&got)==0&&got==token);
  fail_copy=true;assert(call(&file,1,&got)==-EFAULT);assert(call(&file,2,&token)==-EFAULT);assert(call(&file,4,&token)==-EFAULT);fail_copy=false;
 } else if(!strcmp(argv[1],"permission")) {
  assert(access_tokenid_init_module()==0);
  ioctl_add_perm_data add={0};add.token=91;add.perm[0]=1;ioctl_set_get_perm_data bit={0};bit.token=91;
  uid=0;assert(call(&file,5,&add)==-EPERM);uid=1001;assert(call(&file,8,&bit)==-EPERM);
  uid=3020;assert(call(&file,5,&add)==0);assert(allocations==1);assert(call(&file,5,&add)==0&&allocations==1);
  uid=1001;assert(call(&file,7,&bit)==1);bit.op_code=1;assert(call(&file,7,&bit)==0);
  uid=3020;bit.is_granted=true;assert(call(&file,8,&bit)==0);uid=1001;assert(call(&file,7,&bit)==1);
  bit.op_code=2048;assert(call(&file,7,&bit)==-EINVAL);uid=3020;assert(call(&file,8,&bit)==-EINVAL);
  bit.op_code=0;bit.token=999;assert(call(&file,7,&bit)==-ENODATA);assert(call(&file,8,&bit)==-ENODATA);
  for(unsigned i=1;i<500;i++){add.token=1000+i;assert(call(&file,5,&add)==0);}
  add.token=99999;assert(call(&file,5,&add)==-EDQUOT&&allocations==500);
  uint32_t remove=91;assert(call(&file,6,&remove)==0&&allocations==499);assert(call(&file,6,&remove)==0&&allocations==499);
  /* Exit with live nodes must release every allocation, not destroy a live slab. */
  access_tokenid_exit_module();assert(allocations==0&&registrations==0);
 } else if(!strcmp(argv[1],"init_failure")) {
  fail_cache=true;assert(access_tokenid_init_module()==-ENOMEM);assert(registrations==0);
  fail_cache=false;register_error=-EBUSY;assert(access_tokenid_init_module()==-EBUSY);assert(registrations==0);
 } else { assert(0); }
 puts("PASS");return 0;
}
'''
source = shim + '\n' + header + '\n' + driver + '\n' + tests
remote = 'source = ' + repr(source) + '\n' + r'''
from pathlib import Path
import tempfile,subprocess
with tempfile.TemporaryDirectory(prefix='token-driver-test-',dir='/home/zoinve/harmony-virgl-883') as temp:
 p=Path(temp);(p/'test.c').write_text(source)
 subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable',str(p/'test.c'),'-o',str(p/'test')],check=True)
 failures=[]
 for case in ['unsupported','identity','permission','init_failure']:
  r=subprocess.run([str(p/'test'),case],text=True,capture_output=True)
  print(case,r.returncode,r.stdout.strip(),r.stderr.strip())
  if r.returncode:failures.append(case)
 assert not failures,failures
'''
if __name__ == '__main__':
    r = subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,capture_output=True,timeout=90)
    print(r.stdout,r.stderr)
    raise SystemExit(r.returncode)
