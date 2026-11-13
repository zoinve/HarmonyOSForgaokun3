from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
builder=base/'build-native-original-graphics-boot-019.py'
assert builder.exists(),'missing guarded original-service candidate'
p=runpy.run_path(str(builder))
assert '/vendor/lib64/libbt_vendor.z.so' in p['inner']
assert 'libbt_vendor-sdk-original.so' in p['inner']
assert 'native_fault_capture_018(sample)' in p['inner']
assert p['capture']==p['p']['capture']
payload=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-019')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
