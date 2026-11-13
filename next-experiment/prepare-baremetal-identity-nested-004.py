"""Build the bounded nested-transaction regression; never touch prior probes."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-identity-transactions-003.py'))
source=parent['source']
anchor='        require(command==BR_NOOP||command==BR_TRANSACTION_COMPLETE,"no failed or unexpected Binder event");'
assert source.count(anchor)==1
source=source.replace(anchor,'''        if(command==BR_INCREFS||command==BR_ACQUIRE) {
            struct binder_ptr_cookie reference;
            require(size==sizeof(reference),"Binder reference notification layout");
            memcpy(&reference,reader->data+reader->pos,sizeof(reference));
            binder_write_003(reader->fd,command==BR_INCREFS?BC_INCREFS_DONE:BC_ACQUIRE_DONE,&reference,sizeof(reference));
        } else if(command==BR_RELEASE||command==BR_DECREFS) {
            require(size==sizeof(struct binder_ptr_cookie),"Binder reference release layout");
        } else require(command==BR_NOOP||command==BR_TRANSACTION_COMPLETE,"no failed or unexpected Binder event");''')
source=source.replace('int main(void)',(base/'baremetal-identity-nested-004.h').read_text()+'\nint main(void)')
source=source.replace('    binder_transactions_003(binder,fd);','    binder_transactions_003(binder,fd);\n    binder_nested_004(binder,fd);')
source=source.replace('IDENTITY003_','IDENTITY004_').replace('nested_not_tested=1','nested_tested=1')
payload=parent['payload']
start=payload.index('from pathlib import Path')
payload='source='+repr(source)+'\n'+payload[start:]
payload=payload.replace('baremetal-identity-transactions-003','baremetal-identity-nested-004')
compile(payload,'prepare-nested-004','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=90)
    raise SystemExit(result.returncode)
