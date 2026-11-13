"""Correct the test harness's prohibited second mmap; preserve failed 004 evidence."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-identity-nested-004.py'))
source=parent['source']
changes={
    'static void binder_transactions_003(int manager,int token_fd)': 'static void *binder_transactions_003(int manager,int token_fd)',
    '    munmap(mapping,1024*1024);\n}\n\n/* Actual nested': '    return mapping;\n}\n\n/* Actual nested',
    'static void binder_nested_004(int manager,int token_fd)': 'static void binder_nested_004(int manager,int token_fd,void *mapping)',
    '    void *mapping=mmap(NULL,1024*1024,PROT_READ,MAP_PRIVATE,manager,0);\n    require(mapping!=MAP_FAILED,"nested manager Binder mapping");': '',
    '    binder_transactions_003(binder,fd);\n    binder_nested_004(binder,fd);': '    void *manager_mapping=binder_transactions_003(binder,fd);\n    binder_nested_004(binder,fd,manager_mapping);',
}
for old,new in changes.items():
    assert source.count(old)==1,repr(old)
    source=source.replace(old,new)
source=source.replace('IDENTITY004_','IDENTITY005_')
payload=parent['payload'];start=payload.index('from pathlib import Path')
payload='source='+repr(source)+'\n'+payload[start:]
payload=payload.replace('baremetal-identity-nested-004','baremetal-identity-nested-005')
compile(payload,'prepare-nested-005','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=90)
    raise SystemExit(result.returncode)
