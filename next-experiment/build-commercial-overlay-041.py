from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-040-r2.py')))['payload'].replace("commercial61-native-040-r2","commercial61-native-041").replace("commercial61-native-040","commercial61-native-041").replace("commercial-return-audit-040","commercial-return-audit-041").replace("COMMERCIAL040","COMMERCIAL041").replace("ordered_chain_equals_full_040","ordered_chain_equals_full_041").replace("Reference direct EGL GLES route 040","Original application transaction observation 041")
anchor="'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so',"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"'native-target/graphics016/system/lib64/libcommercial_rs_observer041.so',",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
