"""Correct failed012 diagnostics; preserve service/graphics/storage behavior."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-012.py'))
inner=p['inner'].replace('native-scanout-012','native-scanout-013').replace('NATIVE_PIXELS012','NATIVE_PIXELS013')
# Account/BMS initialization is the unresolved boundary. Keep within hilog's ten-tag limit.
tags='AccountMgrService,OsAccountManager,BMS,BMSInstaller,BMSService,BMSDataMgr,BundleMgrService,AppSpawn,AMS,AbilityManagerService'
inner,n=re.subn(r'"-T","[^"]+"','"-T","'+tags+'"',inner,count=1)
assert n==1
anchor='    pid_t observer = fork();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
    int capture_fd=open("/data/native-scanout-013.ppm",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0600);
    if(capture_fd<0 || fchmod(capture_fd,0600) || fchown(capture_fd,3036,3036) || close(capture_fd))fail("composer capture file");
'''+anchor)
capture=p['capture']
capture=capture.replace('if(ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync)){errno=saved;return;}',
    'if(ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync)){native_trace_007("scanout_capture_read_sync",-errno);errno=saved;return;}')
capture=capture.replace('/data/native-scanout-012.tmp','/data/native-scanout-013.ppm').replace('O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC','O_WRONLY|O_TRUNC|O_CLOEXEC')
capture=capture.replace('bool good=fd>=0;','bool good=fd>=0; if(!good)native_trace_007("scanout_capture_open",-errno);')
capture=capture.replace('if(good)rename("/data/native-scanout-013.ppm","/data/native-scanout-012.ppm");',
    'native_trace_007(good?"scanout_capture_success":"scanout_capture_failed",int(buffer.fb));')
assert 'rename(' not in capture
outer=p['outer'].replace('native-original-012-%s','native-original-013-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+repr(p['p']['wrapper'])+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-012','native-original-graphics-boot-013')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
