"""Provide the original ABI's real shmem-backed ashmem device in target boot only."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=runpy.run_path(str(base/'build-native-original-graphics-boot-009.py'))
inner=p['inner'].replace('COMPOSER_SRV,Composer,RSScreenPreprocessor','DISP_HDI_COMP,DISP_CMD,COMPOSER_SRV,Composer,RSScreenPreprocessor')
outer=p['outer'].replace('native-original-009-%s','native-original-010-%s')
needle='    if(mount("/dev/nvme0n1p2","/mnt/ubuntu","ext4",'
assert outer.count(needle)==1
load='''    int ash=open("/hmos_ashmem.ko",O_RDONLY|O_CLOEXEC);
    if(ash<0){dprintf(1,"NATIVE_ASHMEM010 module_open_failed errno=%d\\n",errno);return;}
    int loaded=syscall(SYS_finit_module,ash,"",0);int saved=errno;close(ash);
    if(loaded){dprintf(1,"NATIVE_ASHMEM010 module_load_failed errno=%d\\n",saved);return;}
    struct stat ashdev;
    if(stat("/dev/ashmem",&ashdev) || !S_ISCHR(ashdev.st_mode)){
        dprintf(1,"NATIVE_ASHMEM010 real_device_missing errno=%d\\n",errno);return;
    }
    dprintf(1,"NATIVE_ASHMEM010 loaded=1 device=%u:%u mode=%o\\n",major(ashdev.st_rdev),minor(ashdev.st_rdev),ashdev.st_mode);
'''
outer=outer.replace(needle,load+needle)
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-009','native-original-graphics-boot-010')
needle="file('init',work/'init',0o755)"
assert payload.count(needle)==1
payload=payload.replace(needle,"module=root/'native-ashmem-module-001/hmos_ashmem.ko'\nassert sha(module)=='96aa0454293da0f70791c73d2703e71b79c4ecfc7a003b7f002500aadf0b7322'\nfile('hmos_ashmem.ko',module)\n"+needle)
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
