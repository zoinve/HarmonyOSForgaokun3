"""Diagnose observer entry and merged config without altering original service identities."""
from pathlib import Path
import runpy,subprocess
p=runpy.run_path(str(Path(__file__).with_name('build-commercial-native-006.py')))
anchor='        ssize_t profile=read_path("/run/commercial-profile005/profile.log",text,sizeof(text));'
assert p['inner'].count(anchor)==1
extra=r'''
        if(sample<4){
            const char *paths[]={"/run/commercial-profile005","/run/commercial-profile005/profile.log","/system/bin/commercial-samgr005"};
            for(unsigned q=0;q<3;++q){
                struct stat st;int r=lstat(paths[q],&st);int error=errno;
                dprintf(commercial_diag_fd003,"COMMERCIAL007_STAT path=%s result=%d errno=%d uid=%u gid=%u mode=%o\n",paths[q],r,error,r?0:st.st_uid,r?0:st.st_gid,r?0:(unsigned)st.st_mode);
            }
            ssize_t merged=read_path("/system/etc/init/samgr_standard.cfg",text,sizeof(text));
            if(merged>0)dprintf(commercial_diag_fd003,"COMMERCIAL007_MERGED sample=%u bytes=%zd\n%s\n",sample,merged,text);
        }
'''
inner=p['inner'].replace(anchor,extra+anchor,1)
outer=p['outer'].replace('commercial61-native-006-%s','commercial61-native-007-%s').replace('COMMERCIAL006','COMMERCIAL007')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-006','commercial61-native-007').replace("root/'commercial-profile-005'","root/'commercial-profile-007'")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
