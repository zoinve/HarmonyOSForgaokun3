"""Read actual observer identity, and stop retrying a deterministic genuine SAMGR rejection."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-043.py')))
source=parent['source']
anchor='static int samgr_ping_030(void)'
assert source.count(anchor)==1
source=source.replace(anchor,Path(__file__).with_name('baremetal-samgr-reply-action-044.h').read_text()+'\n'+anchor)
anchor='    int received = 0, result = -1;'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    int actual_reply = 0;')
anchor='                char reply_hex[131073];'
assert source.count(anchor)==1
source=source.replace(anchor,'''                actual_reply = 1;
                errno = 0;
                int token_fd = open("/dev/access_token_id", O_RDONLY | O_CLOEXEC);
                uint64_t own_token = 0;
                int token_rc = token_fd < 0 ? -1 : ioctl(token_fd, _IOR('A',1,uint64_t), &own_token);
                int token_errno = errno;
                if (token_fd >= 0) close(token_fd);
                int type_flag = token_rc ? -2 : own_token ? (int)((own_token >> 27) & 3) : -1;
                dprintf(1,"ORIGINAL_INIT044_CALLER_IDENTITY available=%d self_token=%016llx original_sdk_type_flag=%d read_errno=%d tokens_modified=0\\n",
                    token_rc==0,(unsigned long long)own_token,type_flag,token_errno);
'''+anchor)
anchor='    return received && result == 0;'
assert source.count(anchor)==1
source=source.replace(anchor,'    return samgr_reply_action_044(received, actual_reply, result);')
anchor='        if (samgr_ping_030()) {'
assert source.count(anchor)==1
source=source.replace(anchor,'''        int reply_action = samgr_ping_030();
        if (reply_action < 0) {
            observer_require_039(read_path("/sys/fs/selinux/enforce", enforcing, sizeof(enforcing)) > 0 &&
                                  enforcing[0]=='1', "enforcing after rejected genuine reply");
            dprintf(1,"ORIGINAL_INIT044_MANAGER_LIST_REJECTED terminal=1 enforcing=1 tokens_modified=0 full_services_ready=0\\n");
            _exit(2);
        }
        if (reply_action > 0) {''')
source=source.replace('ORIGINAL_INIT043_','ORIGINAL_INIT044_')
payload='source='+repr(source)+'\nrequest_evidence='+repr(parent['request_evidence'])+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-043','baremetal-sdk-original-init-044')
compile(payload,'original-init-044-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
