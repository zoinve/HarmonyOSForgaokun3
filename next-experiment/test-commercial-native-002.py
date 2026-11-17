"""Check the narrow commercial boot change; this is not desktop acceptance."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
builder=base/'build-commercial-native-002.py'
assert builder.is_file(),'missing minimal commercial startup adaptation'
p=runpy.run_path(str(builder));s=p['inner'];old=p['p']['inner']
assert 'chown("/data/local/tmp/l410-vulkan-r18",1003,1000)' in s
assert 'commercial_early_kernel002();' in s
assert s.index('commercial_early_kernel002();',s.index('int main(void)')) < s.index('execve(arguments[0]')
assert '"/lib/ld-musl-aarch64.so.1","--list","/vendor/bin/hdf_devmgr"' in s
assert 'init.svc.hdf_devmgr' in s and 'init.svc.render_service' in s
assert '"/system/bin/init", "--second-stage"' in s
assert 'commercial61-original-001/' in p['outer']
assert 'left033=420' in p['outer'] and 'elapsed033<240' in p['outer']
for forbidden in ['graphics_provider_050','graphics_egl_054','setuid(','setgid(','LD_PRELOAD=','libcursor_drawing_adapter']:
 assert forbidden not in s,forbidden
assert 'commercial61-native-002' in p['payload']
assert 'execve(arguments[0], arguments, environment);' in old
print('PASS: original commercial init/libraries/identities retained; missing log directory and bounded passive startup evidence only')
