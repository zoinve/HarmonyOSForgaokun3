"""Connect the actual original blue_host UID to the real native QCA controller."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-021.py'))
inner=p['inner'];capture=p['capture']
anchor='    dprintf(1,"NATIVE_BT019 fail_closed_vendor=1 original_services_unmodified=1 native_bluetooth_support_claimed=0\\n");'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
    int endpoint=open("/vendor/lib64/harmony-graphics/native-bt-broker.sock",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0600);
    if(endpoint<0 || close(endpoint) ||
       mount("/native-bt-broker.sock","/vendor/lib64/harmony-graphics/native-bt-broker.sock",NULL,MS_BIND,NULL))fail("real QCA broker endpoint bind");
    dprintf(1,"NATIVE_BT022 original_uid_preserved=1 real_hci_bridge_installed=1 readiness_not_inferred=1\n");
''')
outer=p['outer'].replace('native-original-021-%s','native-original-022-%s')
start=outer.index('    char *qca_reset[]=')
end=outer.index('    int ash=',start)
outer=outer[:start]+'    dprintf(1,"NATIVE_QCA022 power_status=%d uart_status=%d\\n",power_status,uart_status);\n'+outer[end:]
anchor='        static char stack[1024*1024] __attribute__((aligned(16)));'
assert outer.count(anchor)==1
outer=outer.replace(anchor,r'''
        pid_t broker=fork();
        if(broker==0){execl("/native-qca-broker-022","native-qca-broker-022","/native-target/native-bt-broker.sock",NULL);_exit(90);}
        int ready=0;
        for(unsigned i=0;i<50 && broker>0;++i){
            struct stat node;
            if(!lstat("/native-target/native-bt-broker.sock",&node) && S_ISSOCK(node.st_mode) && node.st_uid==3021){ready=1;break;}
            usleep(100000);
        }
        if(!ready){if(broker>0){kill(broker,SIGKILL);waitpid(broker,NULL,0);}dprintf(1,"NATIVE_QCA022 broker_not_ready=1\n");return;}
'''+anchor)
anchor='    }else dprintf(1,"NATIVE_ORIGINAL_REFUSED loop_setup errno=%d\\n",errno);'
assert outer.count(anchor)==1
outer=outer.replace(anchor,'        kill(broker,SIGKILL);waitpid(broker,NULL,0);\n'+anchor)
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
prefix=payload[:offset];wrapper=prefix[prefix.index('WRAPPER=')+len('WRAPPER='):prefix.index('\nCAPTURE=')]
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+wrapper+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-021','native-original-graphics-boot-022')
start=payload.index('\nbt_parent=project/')
end=payload.index('\nbt_header=project/',start)
payload=payload[:start]+"\nbt_source=project/'next-experiment/native-qca-vendor-022.c'"+payload[end:]
payload=payload.replace('honest initialization failure when SDK virtio transport is absent; not native QCA support; no service identities or abort handling changed','real QCA H4 bridge; no command translation; original service identities and abort handling unchanged')
extra=r'''
broker_source=project/'next-experiment/native-qca-broker-022.c'
broker_binary=work/'native-qca-broker-022'
run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(broker_source),'-o',str(broker_binary)])
file('native-qca-broker-022',broker_binary,0o755)
with (local/'qca-bridge.json').open('x') as f:
 json.dump(dict(broker_source_sha256=sha(broker_source),broker_sha256=sha(broker_binary),vendor_source_sha256=sha(bt_source),vendor_sha256=sha(bt_out),allowed_client_uid=3021,server_uid=0,hci_channel='USER',hci_device=0,command_translation=False,original_service_credentials_modified=False,ubuntu_bluetooth_modified=False),f,indent=2)
'''
anchor="file('init',work/'init',0o755)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
