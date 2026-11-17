from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-035.py'))) ['payload']
payload=payload.replace('commercial61-native-035','commercial61-native-036').replace('ordered_chain_equals_full_035','ordered_chain_equals_full_036')
anchor="'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so'}"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so','native-target/graphics016/system/bin/aurora','native-target/graphics016/system/bin/aurora/samgr-service-probe','native-target/graphics016/system/bin/aurora/appspawn-reference-namespace'}")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
