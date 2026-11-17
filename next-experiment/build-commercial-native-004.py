"""Add only the absent MateBook board import; preserve original HDF service and libraries."""
from pathlib import Path
import json,runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-003.py'))
board=json.dumps({'import':['/vendor/etc/init/hdf_devmgr.cfg']},separators=(',',':'))+'\n'
helper=r'''
static void commercial_board004(void)
{
    struct stat st;
    if(!lstat("/vendor/etc/init.matebookego.cfg",&st) || errno!=ENOENT)
        fail("commercial board configuration must be absent");
    directory("/run/commercial-vendor004",0700);
    directory("/run/commercial-vendor004/upper",0755);
    directory("/run/commercial-vendor004/work",0700);
    directory("/run/commercial-vendor004/upper/etc",0755);
    const char data[]=BOARD004;
    int fd=open("/run/commercial-vendor004/upper/etc/init.matebookego.cfg",
        O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0644);
    if(fd<0)fail("commercial board configuration create");
    if(write(fd,data,sizeof(data)-1)!=(ssize_t)(sizeof(data)-1) || close(fd))
        fail("commercial board configuration write");
    const char *options="lowerdir=/vendor,upperdir=/run/commercial-vendor004/upper,workdir=/run/commercial-vendor004/work";
    if(mount("overlay","/vendor","overlay",MS_RDONLY,options))
        fail("commercial read-only vendor board overlay");
    dprintf(1,"COMMERCIAL004_BOARD original_hdf_config_import=1 original_service_identity=1 original_libraries=1 ram_only=1\n");
}
'''.replace('BOARD004',json.dumps(board))
inner=p['inner'].replace('int main(void)',helper+'\nint main(void)',1)
anchor='    /* Images are already mounted from verified immutable loop devices.'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'    commercial_board004();\n'+anchor,1)
outer=p['outer'].replace('commercial61-native-003-%s','commercial61-native-004-%s').replace('COMMERCIAL003','COMMERCIAL004')
payload=p['payload'];assert payload.count('inner='+repr(p['inner']))==1 and payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-003','commercial61-native-004')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
