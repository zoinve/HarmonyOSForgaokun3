"""Prepare a real-kernel regression for the diagnostic-only read probe."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-identity-connector-008.py'))
source=parent['source'];anchor='    pid_t sdk_child=fork();';assert source.count(anchor)==1
source=source.replace(anchor,'''    pid_t native_child=fork();require(native_child>=0,"fork native diagnostic read probe");
    if(!native_child){close(binder);close(fd);execl("/sdk/native-probe","native-probe",NULL);_exit(92);}
    require(child_status(native_child),"native diagnostic read probe and cleanup");
    require(ioctl(fd,SELF_GET,&out)==0&&out==value,"diagnostic read probe preserves parent token");
'''+anchor).replace('IDENTITY008_','IDENTITY009_')
sdk_source=parent['sdk_source'].replace('SDK008_','SDK009_').replace('IPC008_','IPC009_')
payload=parent['payload'];payload=payload[payload.index('\nfrom pathlib import Path')+1:]
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+payload
payload=payload.replace('baremetal-identity-connector-008','baremetal-identity-native-read-009')
anchor="(work/'init.c').write_text(source);(work/'sdk-probe.c').write_text(sdk_source)";assert payload.count(anchor)==1
addition="""native_source=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/baremetal-native-identity-read-001.c').read_bytes()
(work/'native-probe.c').write_bytes(native_source)
run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/'native-probe.c'),'-o',str(sdk/'native-probe')],'native-compile')
"""
payload=payload.replace(anchor,addition+anchor)
compile(payload,'prepare-native-read-009','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(result.returncode)
