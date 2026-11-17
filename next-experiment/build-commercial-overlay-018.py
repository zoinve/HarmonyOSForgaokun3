"""Reuse immutable hardware archives; add only launchers and new harness code."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-017.py')))['payload']
payload=payload.replace("work=root/'commercial61-native-017';local=base.parent/'reports/commercial61-native-017'","work=root/'commercial61-native-018';local=base.parent/'reports/commercial61-native-018'")
start=payload.index('added={n for n in new')
end=payload.index("data=b''.join(member",start)
payload=payload[:start]+'''\
directory_patch=parse(root/'commercial61-native-017/minimal-overlay.img')
state=dict(old)
for archive in [directory_patch,broken]:state.update(archive)
patch={n:new[n] for n in new if n not in state or new[n]!=state[n]}
assert set(patch)=={'init','native-target/bootstrap','native-target/graphics016/system/bin/l410_launch_appspawn_r18_namespace.sh'}
for name in sorted(patch):
 for parent in Path(name).parents:
  if str(parent)=='.':continue
  assert str(parent) in state and stat.S_ISDIR(state[str(parent)][0]),('missing parent at extraction',name,str(parent))
 state[name]=patch[name]
assert state==new,'ordered 018 chain differs from full archive'
'''+payload[end:]
payload=payload.replace("'commercial61-native-017/initrd.img'],","'commercial61-native-018/initrd.img'],")
payload=payload.replace('ordered_chain_equals_full_017=True','ordered_chain_equals_full_018=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
