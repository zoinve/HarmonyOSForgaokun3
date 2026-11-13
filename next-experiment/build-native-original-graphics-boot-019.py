"""Report missing emulator Bluetooth transport as failure, not successful init."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-018.py'))
inner=p['inner'];capture=p['capture']
anchor='    graphics_egl_054();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+r'''
    int bt=open("/vendor/lib64/harmony-graphics/libbt_vendor-sdk-original.so",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0644);
    if(bt<0 || close(bt))fail("original Bluetooth library bind target");
    const char *bt_from[]={"/libbt_vendor-sdk-original.so","/libbt_vendor-guard-019.so"};
    const char *bt_to[]={"/vendor/lib64/harmony-graphics/libbt_vendor-sdk-original.so","/vendor/lib64/libbt_vendor.z.so"};
    for(unsigned i=0;i<2;++i){
        if(mount(bt_from[i],bt_to[i],NULL,MS_BIND,NULL) ||
           mount(NULL,bt_to[i],NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))fail("Bluetooth guarded vendor bind");
    }
    dprintf(1,"NATIVE_BT019 fail_closed_vendor=1 original_services_unmodified=1 native_bluetooth_support_claimed=0\n");
''')
outer=p['outer'].replace('native-original-018-%s','native-original-019-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
prefix=payload[:offset];wrapper=prefix[prefix.index('WRAPPER=')+len('WRAPPER='):prefix.index('\nCAPTURE=')]
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+wrapper+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-018','native-original-graphics-boot-019')
extra=r'''
bt_source=project/'next-experiment/native-bt-vendor-guard-019.c'
bt_header=project/'references/L410-HarmonyOS-Adaptations/bluetooth/ohos_bt_vendor_abi.h'
bt_original=work/'libbt_vendor-sdk-original.so'
subprocess.run(['debugfs','-R',f'dump /lib64/libbt_vendor.z.so {bt_original}','/mnt/d/Download/pc_all_arm/vendor.img'],capture_output=True,text=True,check=True)
assert b'/dev/hwbt' in bt_original.read_bytes()
bt_out=work/'libbt_vendor-guard-019.so'
command=[str(root/'window-bridge/toolchain/ohos-cc'),'-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-I'+str(bt_header.parent),str(bt_source),'-ldl','-Wl,--no-undefined,-soname,libbt_vendor.z.so','-o',str(bt_out)]
r=subprocess.run(command,capture_output=True,text=True)
(local/'bt-compile.stdout').write_text(r.stdout);(local/'bt-compile.stderr').write_text(r.stderr)
assert r.returncode==0,r.stderr
file('native-target/libbt_vendor-sdk-original.so',bt_original)
file('native-target/libbt_vendor-guard-019.so',bt_out)
with (local/'bluetooth-guard.json').open('x') as f:
 json.dump(dict(source_sha256=sha(bt_source),abi_header_sha256=sha(bt_header),original_sha256=sha(bt_original),guard_sha256=sha(bt_out),command=command,scope='honest initialization failure when SDK virtio transport is absent; not native QCA support; no service identities or abort handling changed'),f,indent=2)
'''
anchor="file('init',work/'init',0o755)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
