"""Priorities: real touchscreen orientation, missing USB PHY/HID bringup, settings diagnosis."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-025.py'))
inner=p['inner'];outer=p['outer'].replace('native-original-025-%s','native-original-026-%s')
anchor='    char *qca_power[]='
assert outer.count(anchor)==1
outer=outer.replace(anchor,r'''
    const char *input_modules[]={"phy_qcom_snps_femto_v2","phy_qcom_qmp_usb","hid_multitouch"};
    for(unsigned i=0;i<3;++i){
        char *args[]={"/sbin/modprobe","--config","/etc/modprobe.d",(char *)input_modules[i],NULL};
        int rc=probe(input_modules[i],args,8);
        dprintf(1,"NATIVE_INPUT026 module=%s status=%d\n",input_modules[i],rc);
    }
    sleep(2);
'''+anchor)
anchor='        diagnostic_state_002(sample);'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+r'''
        if(sample==3 || sample==9 || sample==11){
            dprintf(1,"NATIVE_INPUT026 inventory sample=%u\n",sample);
            diagnostic_file_002(sample,"/proc/bus/input/devices");
            diagnostic_file_002(sample,"/proc/modules");
        }
        if(sample==9){
            pid_t launch=fork();
            if(launch==0){
                alarm(5);dprintf(1,"NATIVE_SETTINGS026 original_aa_start requested=1\n");
                execl("/system/bin/aa","aa","start","-b","com.huawei.hmos.settings","-a","com.huawei.hmos.settings.MainAbility",(char *)NULL);
                dprintf(1,"NATIVE_SETTINGS026 aa_exec_failed errno=%d\n",errno);_exit(127);
            }
        }
''')
inner,n=re.subn(r'"-T","[^"]+"','"-T","Settings,AMS,AbilityManagerService,Ace,ArkCompiler,InputKeyFlow,InputDevice,InputWindowsManager,MMI,InputService"',inner,count=1)
assert n==1
payload=p['payload'].replace('native-original-graphics-boot-025','native-original-graphics-boot-026')
assert 'inner='+repr(p['inner']) in payload and 'outer='+repr(p['outer']) in payload
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
adapt=r'''
touch_patch=runpy.run_path(str(project/'next-experiment/native-touch-dtb-026.py'))
dtb_path=work/'sc8280xp-huawei-gaokun3.dtb'
old_dtb=dtb_path.read_bytes();new_dtb=touch_patch['landscape_dtb'](old_dtb)
dtb_path.write_bytes(new_dtb)
before_props=touch_patch['properties'](old_dtb);after_props=touch_patch['properties'](new_dtb)
changed_keys=[list(k) for k in set(before_props)|set(after_props) if before_props.get(k)!=after_props.get(k)]
assert len(changed_keys)==2
with (local/'touch-orientation-026.json').open('x') as f:
 json.dump(dict(original_dtb_sha256=hashlib.sha256(old_dtb).hexdigest(),target_dtb_sha256=sha(dtb_path),
  changed_properties=changed_keys,logical_axes=[2560,1600],mapping='logical=(physical_y,1599-physical_x)',
  kernel_and_display_timings_unchanged=True,ubuntu_dtb_unchanged=True,human_touch_verified=False),f,indent=2)
'''
anchor='artifacts=[]';assert payload.count(anchor)==1
payload=payload.replace(anchor,'import runpy\n'+adapt+'\n'+anchor)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
