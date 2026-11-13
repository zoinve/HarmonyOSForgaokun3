"""Read authentic sender metadata after an allowed PING; never issue an SA authorization query."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-040.py')))
source=parent['source']
anchor='                memcpy(&tx, events + pos, sizeof(tx));'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''
                struct sender_info_046 {
                    uint64_t token, first, reserved[2], pid;
                } sender = {0};
                _Static_assert(sizeof(sender)==40, "original sender info ABI");
                errno=0;
                int sender_result=ioctl(fd,_IOWR('b',32,struct sender_info_046),&sender);
                int sender_errno=errno;
                dprintf(1,"ORIGINAL_INIT046_REPLY_SENDER result=%d errno=%d token=%016llx first=%016llx pid=%llu reserved0=%llu reserved1=%llu uid=%u tokens_modified=0\\n",
                        sender_result,sender_errno,(unsigned long long)sender.token,
                        (unsigned long long)sender.first,(unsigned long long)sender.pid,
                        (unsigned long long)sender.reserved[0],(unsigned long long)sender.reserved[1],tx.sender_euid);
                require(!sender_result, "read authentic reply sender under unchanged policy");
                require(tx.sender_euid==5555 && sender.pid>1 && sender.pid<=INT32_MAX &&
                        sender.token && !sender.reserved[0] && !sender.reserved[1],
                        "genuine SAMGR reply has nonzero token PID and zero ABI reserved fields");
''')
source=source.replace('ORIGINAL_INIT040_','ORIGINAL_INIT046_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-040','baremetal-sdk-original-init-046')
compile(payload,'original-init-046-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
