"""CPU contract for the private extracted-method bridge, not GPU or HDI evidence."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
generator=base/'baremetal-composer-bridge-001.py'
assert generator.exists(), 'missing extracted composer C bridge'
data=runpy.run_path(str(generator))['build_sources']()
test=r'''
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <unistd.h>
extern int composer_accept001(int,int,uint32_t,uint32_t,uint32_t);
extern int composer_borrow001(void);
extern int composer_clear001(void);
int main(void) {
    assert(composer_borrow001()==-1);
    int fd=open("/dev/zero",O_RDONLY|O_CLOEXEC);assert(fd>=0);
    assert(composer_accept001(fd,-1,13,7,51)==-3);
    assert(composer_borrow001()==-1);
    assert(composer_accept001(fd,-1,13,7,256)==0);
    int held=composer_borrow001();assert(held>=0 && held!=fd);
    assert(fcntl(held,F_GETFD)&FD_CLOEXEC);
    assert(composer_accept001(fd,-1,13,7,UINT32_MAX)==-3);
    assert(composer_borrow001()==held);
    close(fd);char byte=1;assert(read(held,&byte,1)==1 && byte==0);
    assert(composer_clear001()==0 && composer_borrow001()==-1);
    assert(fcntl(held,F_GETFD)==-1 && errno==EBADF);
    assert(composer_clear001()==0);
    return 0;
}
'''
payload='sources='+repr(data)+'\ntest='+repr(test)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='composer-bridge001-') as d:
    p=Path(d)
    for name,text in sources.items():(p/name).write_text(text)
    (p/'test.c').write_text(test)
    subprocess.run(['cc','-Wall','-Wextra','-Werror','-c',str(p/'test.c'),'-o',str(p/'test.o')],check=True)
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-pthread',str(p/'bridge.cpp'),str(p/'test.o'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True,timeout=10)
print('PASS: private C bridge metadata, retained-FD lifetime and clear; CPU_ONLY')
'''
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=45).returncode)
