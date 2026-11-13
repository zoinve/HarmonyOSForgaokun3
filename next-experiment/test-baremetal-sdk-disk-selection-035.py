"""Exercise serial+capacity selection with reversed, missing and ambiguous devices."""
from pathlib import Path
import subprocess

header=Path(__file__).with_name('baremetal-sdk-disk-selection-035.h')
body=r'''
#include <assert.h>
#include "selection.h"
int main(int argc, char **argv) {
    assert(argc==2);char name[32];
    assert(sdk_select_disk_035(argv[1],"sdk-system",7168000,name,sizeof(name))==1);
    assert(!strcmp(name,"vdc"));
    assert(sdk_select_disk_035(argv[1],"sdk-system",2048000,name,sizeof(name))==-1);
    assert(sdk_select_disk_035(argv[1],"missing",7168000,name,sizeof(name))==0);
    char path[1024];snprintf(path,sizeof(path),"%s/vdz",argv[1]);assert(!mkdir(path,0700));
    snprintf(path,sizeof(path),"%s/vdz/serial",argv[1]);FILE *f=fopen(path,"w");assert(f);fputs("sdk-system\n",f);fclose(f);
    snprintf(path,sizeof(path),"%s/vdz/size",argv[1]);f=fopen(path,"w");assert(f);fputs("7168000\n",f);fclose(f);
    assert(sdk_select_disk_035(argv[1],"sdk-system",7168000,name,sizeof(name))==-1);
    return 0;
}
'''
payload='header='+repr(header.read_text())+'\nbody='+repr(body)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='disk035-',dir='/home/zoinve/harmony-virgl-883') as d:
 p=Path(d);(p/'selection.h').write_text(header);(p/'test.c').write_text(body);devices=p/'devices';devices.mkdir()
 for name,serial,size in [('vda','sdk-sysprod',2048000),('vdb','sdk-vendor',204800),('vdc','sdk-system',7168000)]:
  q=devices/name;q.mkdir();(q/'serial').write_text(serial+'\n');(q/'size').write_text(str(size)+'\n')
 subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test'),str(devices)],check=True,timeout=5)
 print('PASS: reverse enumeration selects vdc; wrong capacity, missing serial, and duplicates refused')
'''
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60)
    raise SystemExit(r.returncode)
