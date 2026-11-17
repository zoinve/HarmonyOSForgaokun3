"""Offline commercial capacity/admission and bounded teardown candidate.

No installation or reboot. GPU deployment remains a separate, unverified step.
"""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-008.py'))
assert p['inner'].count('3221225472ULL')==1
inner=p['inner'].replace('3221225472ULL','8589934592ULL').replace('2800000000ULL','7516192768ULL')
outer=p['outer'].replace('commercial61-native-008-%s','commercial61-native-010-%s').replace('COMMERCIAL008','COMMERCIAL010')
assert outer.count('3221225472ULL')==2
outer=outer.replace('3221225472ULL','8589934592ULL')
anchor='#include <signal.h>'
assert outer.count(anchor)==1
outer=outer.replace(anchor,anchor+'\n#include "commercial-safety-010.h"',1)
anchor='        int ram=open("/native-target/scratch-data.ext4",O_RDWR|O_CLOEXEC|O_NOFOLLOW);'
assert outer.count(anchor)==1
admission=r'''
        char memory010[8192];unsigned long long total010=0,available010=0;
        if(read_text("/proc/meminfo",memory010,sizeof(memory010)))okay=0;
        if(okay){
            char *t010=strstr(memory010,"MemTotal:"),*a010=strstr(memory010,"MemAvailable:");
            if(!t010 || !a010 || sscanf(t010,"MemTotal: %llu",&total010)!=1 ||
               sscanf(a010,"MemAvailable: %llu",&available010)!=1 ||
               !commercial_ram_budget010(total010*1024,available010*1024))okay=0;
        }
        dprintf(1,"COMMERCIAL010_RAM_ADMISSION total_kib=%llu available_kib=%llu permitted=%d capacity_bytes=8589934592\n",total010,available010,okay);
        if(!okay){dprintf(1,"COMMERCIAL010_REFUSED insufficient_memory_for_8g_data=1\n");return;}
'''
outer=outer.replace(anchor,admission+anchor,1)
finish=r'''
static void commercial_finish010(void *unused)
{
    (void)unused;
    /* All potentially blocking final evidence writes and filesystem flushing
     * run in the worker, not in the parent responsible for returning Ubuntu. */
    snapshot();
    if(run>=0 && syncfs(run)){dprintf(2,"COMMERCIAL010_SYNCFS_FAILED errno=%d\n",errno);_exit(126);}
    if(run>=0)close(run);
    /* The parent still owns its directory FD. Detach only after successful
     * flushing; avoid EBUSY from that FD without waiting on unrelated mounts. */
    if(mounted && umount2("/mnt/lab",MNT_DETACH))_exit(126);
}
'''
assert outer.count('int main(void)')==1
outer=outer.replace('int main(void)',finish+'\nint main(void)',1)
old=r'''    snapshot();
    if (run >= 0) { close(run); run = -1; }
    if (mounted && umount("/mnt/lab")) dprintf(2, "LAB_UNMOUNT_FAILED errno=%d\n", errno);
    /* Deadline remains a best-effort fallback if unmount itself stalls. */
    dprintf(1,"COMMERCIAL010_STOPPED returning_to_ubuntu=1\n");
    sync();
    reboot(RB_AUTOBOOT);'''
new=r'''    int cleanup010=commercial_bounded010(commercial_finish010,NULL,15000);
    if(run>=0){close(run);run=-1;}
    dprintf(1,"COMMERCIAL010_STOPPED cleanup_status=%d returning_to_ubuntu=1 global_sync_skipped=1 evidence_may_be_incomplete=%d\n",cleanup010,cleanup010!=0);
    reboot(RB_AUTOBOOT);'''
assert outer.count(old)==1
outer=outer.replace(old,new,1)
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-008','commercial61-native-010')
payload=payload.replace('runtime_verified=False)', 'runtime_verified=False,volatile_data_capacity_bytes=8589934592,memory_admission_required=True,final_cleanup_timeout_ms=15000)')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
