from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-016.py').is_file(), 'missing original-service commercial graphics integration'
p=runpy.run_path(str(base/'build-commercial-native-016.py'))
s=p['inner'];o=p['outer']
assert 'commercial_drm016();' in s and '/sys/class/drm/' in s
assert 'makedev(maj,min)' in s and 'st.st_rdev!=makedev(maj,min)' in s
assert 'commercial_vendor016();' in s and 'commercial_system016();' in s
assert s.index('commercial_vendor016();')<s.index('lowerdir=/vendor,upperdir=')
assert s.index('commercial_system016();')<s.index('lowerdir=/system,upperdir=')
assert 'original_service_credentials_unchanged=1' in s
assert 'commercial61-original-001' in o and '8589934592' in o
assert 'commercial_bounded010(commercial_finish010,NULL,15000)' in o
assert 'left033=210' in o and 'elapsed033<90' in o
assert 'execve(arguments[0], arguments, environment)' in s and '"/system/bin/init", "--second-stage"' in s
assert 'libc++_shared.so' not in s and 'l410_mali_r18_gpu_helper' not in s
print('PASS: original-service hardware overlay, real sysfs DRM nodes, original images and bounded 8GiB safety retained; runtime pending')
