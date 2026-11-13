"""Safely read original initialized descriptor, including legitimate heap-backed strings."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-parcel-041.py')))
sdk_source=parent['sdk_source']
old='''    check(descriptor_address>=(uintptr_t)proxy_info.dli_fbase&&
          descriptor_address+2*(descriptor_view[0]+1)<=(uintptr_t)proxy_info.dli_fbase+0x30000,
          "descriptor string belongs to original proxy mapped image");
    const uint16_t *descriptor=(const uint16_t *)descriptor_address;'''
new='''    /* Original C++ constructors may allocate descriptor storage on the heap.
       Read only our own memory through a bounded kernel-checked read. */
    check(descriptor_address>0&&descriptor_address<INT64_MAX-256,
          "original descriptor pointer is a bounded userspace address");
    uint16_t descriptor_copy[128];
    size_t descriptor_bytes=2*(descriptor_view[0]+1);
    int self_mem=open("/proc/self/mem",O_RDONLY|O_CLOEXEC);
    check(self_mem>=0&&pread(self_mem,descriptor_copy,descriptor_bytes,(off_t)descriptor_address)==(ssize_t)descriptor_bytes,
          "read bounded original descriptor storage");
    close(self_mem);
    const uint16_t *descriptor=descriptor_copy;'''
assert sdk_source.count(old)==1
sdk_source=sdk_source.replace(old,new).replace('PARCEL041_','PARCEL042_')
payload=parent['payload'];payload=payload[payload.index('\nfrom pathlib import Path')+1:]
payload='source='+repr(parent['source'])+'\nsdk_source='+repr(sdk_source)+'\n'+payload
payload=payload.replace('baremetal-sdk-parcel-041','baremetal-sdk-parcel-042')
compile(payload,'prepare-parcel-042','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(r.returncode)
