"""Keep original SDK /usr/system customization paths valid in original sandboxes."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-014.py'))
inner=p['inner'];capture=p['capture']
anchor='    const char *dac_paths[]='
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
    directory("/mnt",0755);directory("/mnt/sandbox",0755);
    const char *sandboxes[]={"/mnt/sandbox/system","/mnt/sandbox/chipset"};
    for(unsigned i=0;i<2;++i){
        char usr[128],alias[128];
        directory(sandboxes[i],0755);
        snprintf(usr,sizeof(usr),"%s/usr",sandboxes[i]);directory(usr,0755);
        snprintf(alias,sizeof(alias),"%s/usr/system",sandboxes[i]);
        if(symlink("/system",alias))fail("original SDK sandbox layout alias");
        dprintf(1,"NATIVE_LAYOUT015 path=%s target=/system original_sandbox=1\n",alias);
    }
'''+anchor)
outer=p['outer'].replace('native-original-014-%s','native-original-015-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+repr(p['p']['p']['p']['wrapper'])+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-014','native-original-graphics-boot-015')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
