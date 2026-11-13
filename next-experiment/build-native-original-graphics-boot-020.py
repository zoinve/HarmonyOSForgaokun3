"""Diagnostic-only follow-up: observable native Bluetooth failure propagation."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-019.py'))
capture=p['capture'];inner=p['inner']
anchor='    graphics_egl_054();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+r'''
    int bt_trace=open("/data/native-bt-020.trace",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0666);
    if(bt_trace<0 || fchmod(bt_trace,0666) || close(bt_trace))fail("Bluetooth failure trace file");
''')
anchor='        diagnostic_state_002(sample);'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''        if(sample==2 || sample==5 || sample==8 || sample==11){
            dprintf(1,"NATIVE_BT020_TRACE sample=%u\n",sample);
            diagnostic_file_002(sample,"/data/native-bt-020.trace");
        }
'''+anchor)
inner,n=re.subn(r'"-T","[^"]+"','"-T","bt_hci,HDF_LOG_TAG,virtio_bt,BluetoothHost,BluetoothService,BT_SERVICE,FaultLogger,DfxSignalHandler,SAMGR,SAFWK"',inner,count=1)
assert n==1
outer=p['outer'].replace('native-original-019-%s','native-original-020-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
prefix=payload[:offset];wrapper=prefix[prefix.index('WRAPPER=')+len('WRAPPER='):prefix.index('\nCAPTURE=')]
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+wrapper+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-019','native-original-graphics-boot-020')
anchor="bt_source=project/'next-experiment/native-bt-vendor-guard-019.c'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,r'''
bt_parent=project/'next-experiment/native-bt-vendor-guard-019.c'
bt_text=bt_parent.read_text()
bt_anchor='    errno=saved;return -1;'
assert bt_text.count(bt_anchor)==1
bt_text=bt_text.replace(bt_anchor,'''+'r'+"'''"+r'''
    fd=open("/data/native-bt-020.trace",O_WRONLY|O_APPEND|O_CLOEXEC|O_NOFOLLOW);
    if(fd>=0){dprintf(fd,"NATIVE_BT020 unavailable reason=%s errno=%d uid=%u success_callback=0\n",reason,saved,(unsigned)getuid());close(fd);}
'''+"'''"+r'''+bt_anchor)
bt_source=work/'native-bt-vendor-guard-020.c'
bt_source.write_text(bt_text)
(local/'native-bt-vendor-guard-020.c').write_text(bt_text)
''')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
