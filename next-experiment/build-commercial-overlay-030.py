from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-029.py')))['payload']
payload=payload.replace('commercial61-native-029','commercial61-native-030').replace('ordered_chain_equals_full_029','ordered_chain_equals_full_030')
payload=payload.replace("work=root/'commercial61-native-030';", "work=root/'commercial61-native-030-r2';",1)
anchor="'native-target/graphics016/system/lib64/libEGL_impl.so'}"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"'native-target/graphics016/system/lib64/libEGL_impl.so','native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so'}",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
