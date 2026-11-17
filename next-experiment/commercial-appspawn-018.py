"""Adapt only the original Kirin-specific launcher, retaining original appspawn."""
import shlex

def repair(original):
    assert original.count('\nexec ')==1
    argv=shlex.split(original.replace('\\\n','').split('exec ',1)[1])
    assert argv[:3]==['/system/bin/l410_appspawn_r18_namespace_exec',
                     '/data/local/tmp/l410-sceneboard-r18-passthrough-v2',
                     '/system/bin/appspawn']
    assert '-mode appspawn' in argv and any('--sandbox-switch on' in x for x in argv)
    return '#!/system/bin/sh\nset -eu\nexec '+shlex.join(argv[2:])+'\n'
