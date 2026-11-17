"""Observe genuine UI/provider behavior with early namespace pins and bounded logs."""


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


def outer235(source):
    path = '/commercial61-native-206/bootstrap-runtime087'
    assert source.count(path) == 5
    source = source.replace(path, '/commercial61-native-235/bootstrap-runtime087')
    source = once(source, '#include "settings-launch-206.h"', '')
    source = once(source, '                if(i==10)settings206_start(child);\n', '')
    source = once(source, '                if(elapsed033%15==0)settings206_start(child);\n', '')
    old = ('int state=0;pid_t got=waitpid(child,&state,WNOHANG);\n'
           '                dprintf(1,"NATIVE_ORIGINAL_SAMPLE index=%u child=%d status=%d\\n",i,got,state);')
    new = ('persistent172_pin(child);\n'
           '                siginfo_t info235;memset(&info235,0,sizeof(info235));\n'
           '                int observed235=waitid(P_PID,child,&info235,WEXITED|WNOHANG|WNOWAIT);\n'
           '                pid_t got=observed235<0?-1:info235.si_pid;\n'
           '                dprintf(1,"NATIVE_ORIGINAL_SAMPLE index=%u child=%d waitid_code=%d observed_exit_status=%d not_reaped=1\\n",i,got,info235.si_code,info235.si_status);')
    source = once(source, old, new)
    source = once(source, 'for(unsigned elapsed033=70;elapsed033<720;++elapsed033){\n',
        'for(unsigned elapsed033=70;elapsed033<720;++elapsed033){\n                persistent172_pin(child);\n')
    source = once(source, 'static unsigned snapshot_id;\n',
        'static unsigned snapshot_id;\nstatic char snapshot235_previous[40], snapshot235_older[40];\n')
    old = '    close(fd);\n    dprintf(2, "SNAPSHOT name=%s failed=%d\\n", name, failed);'
    new = '''    close(fd);
    /* Retain two successful cumulative snapshots; never discard prior evidence on write failure. */
    if (!failed) {
        if (snapshot235_older[0] && unlinkat(run,snapshot235_older,0))
            dprintf(2,"SNAPSHOT235_PRUNE_FAILED errno=%d\\n",errno);
        snprintf(snapshot235_older,sizeof(snapshot235_older),"%s",snapshot235_previous);
        snprintf(snapshot235_previous,sizeof(snapshot235_previous),"%s",name);
        if (fsync(run)) dprintf(2,"SNAPSHOT235_DIRECTORY_SYNC_FAILED errno=%d\\n",errno);
    }
    dprintf(2, "SNAPSHOT name=%s failed=%d\\n", name, failed);'''
    return once(source, old, new)
