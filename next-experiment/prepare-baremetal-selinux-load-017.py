"""Restore original console label after policy activation, as real init must do."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-selinux-load-016.py')))
source=parent['source']
anchor='    close(context_fd);'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''
    require(!setxattr("/dev/console", "security.selinux", console_context,
                     sizeof(console_context), 0), "restore original console label after policy activation");
    char actual_context[128] = {0};
    require(getxattr("/dev/console", "security.selinux", actual_context, sizeof(actual_context)-1) > 0 &&
            !strcmp(actual_context, console_context), "verify original console context");
''').replace('SELINUX016_','SELINUX017_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-load-016','baremetal-selinux-load-017')
compile(payload,'selinux-017-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
