"""Audit full archive difference, install only changed init and composer bytes."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
payload=runpy.run_path(str(base/'build-native-return-overlay-033.py'))['payload']
payload=payload.replace('native-original-graphics-boot-033','native-original-graphics-boot-034')
payload=payload.replace("{'init','native-target/scratch-data.ext4'}", "{'init','native-target/scratch-data.ext4','native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'}")
payload=payload.replace("raw=member('init',new['init'][0],new['init'][1],1)+member('TRAILER!!!',0,b'',2)","names=['init','native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so']\nraw=b''.join(member(n,new[n][0],new[n][1],i+1) for i,n in enumerate(names))+member('TRAILER!!!',0,b'',3)")
payload=payload.replace("assert parse(dest)=={'init':new['init']}","assert parse(dest)=={n:new[n] for n in names}")
payload=payload.replace("only_changed_member=['init']",'only_changed_member=names')
payload=payload.replace('fresh_unused_033_scratch_not_installed','fresh_unused_034_scratch_not_installed')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
