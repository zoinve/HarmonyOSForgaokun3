"""Pin the additive board import; original commercial service definitions stay intact."""
from pathlib import Path
import json,runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-004.py').is_file(),'missing minimal MateBook board import'
p=runpy.run_path(str(base/'build-commercial-native-004.py'))
assert json.loads(p['board'])=={'import':['/vendor/etc/init/hdf_devmgr.cfg']}
assert 'services' not in json.loads(p['board']) and 'jobs' not in json.loads(p['board'])
s=p['inner']
assert 'MS_RDONLY,options' in s and 'lowerdir=/vendor,upperdir=/run/commercial-vendor004/upper' in s
assert s.index('    commercial_board004();') < s.index('    if(mount("/commercial-mounts.cfg"')
assert 'O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW' in s
assert 'execve(arguments[0], arguments, environment);' in s
assert 'commercial_diag_fd003=fcntl(199,F_DUPFD_CLOEXEC,200)' in s
assert 'commercial61-original-001/' in p['outer'] and 'commercial61-native-004-%s' in p['outer']
for forbidden in ['graphics_provider050','graphics_egl054','setuid(','setgid(','LD_PRELOAD=']:
    assert forbidden not in s,forbidden
assert 'left033=420' in p['outer'] and 'elapsed033<240' in p['outer']
print('PASS: one original HDF import, RAM-only read-only vendor overlay, unchanged identity/libs, bounded return')
