"""Regression: execute Mesa002's actual compiled comparison function under OHOS."""
from pathlib import Path

base=Path(__file__).resolve().parent
source=(base/'run-baremetal-fd-identity-probe-001.py').read_text()
source=source.replace('baremetal-fd-identity-probe-001','baremetal-fd-identity-probe-002')
source=source.replace('fd-identity-transfer-001','fd-identity-transfer-002')
source=source.replace('next-experiment/baremetal-fd-identity-probe-002.c','next-experiment/baremetal-fd-identity-probe-001.c')
anchor="source=(base/'next-experiment/baremetal-fd-identity-probe-001.c').read_text()"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''\nsource=source.replace('int main(void)', 'extern int os_same_file_description(int, int);\\nint main(void)')
source=source.replace('syscall(SYS_kcmp,getpid(),getpid(),0,first,duplicate)', 'os_same_file_description(first,duplicate)')
source=source.replace('syscall(SYS_kcmp,getpid(),getpid(),0,first,independent)', 'os_same_file_description(first,independent)')
source=source.replace('FD_IDENTITY001', 'FD_IDENTITY002')
''')
anchor="str(work/'probe.c'),'-o',str(work/'probe')"
assert source.count(anchor)==1
source=source.replace(anchor,"str(work/'probe.c'),str(root/'baremetal-mesa-freedreno-002/build/src/util/libmesa_util.a.p/os_file.c.o'),'-o',str(work/'probe')")
compile(source,'fd-identity002-regression','exec')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
