"""Isolation/provenance gates; not proof that commercial services reach desktop."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
builder=base/'build-commercial-native-001.py'
assert builder.exists(),'missing commercial-only boot harness'
p=runpy.run_path(str(builder));inner=p['inner'];outer=p['outer']
assert 'execve(arguments[0], arguments, environment)' in inner
assert '"/system/bin/init", "--second-stage"' in inner
assert 'readonly_image("commercial-chipprod", 2097152, "/chip_prod")' in inner
assert 'readonly_image("commercial-system", 16777216, "/usr")' in inner
assert 'harmony.commercial=1' in inner
assert 'fstab.l410-second-stage' in inner and 'commercial-mounts.cfg' in inner
assert 'left033=420' in outer and 'elapsed033<240' in outer
assert 'commercial61-original-001/' in outer and 'chipprod.img' in outer
assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET' in outer
for x in ['graphics_provider_050','graphics_egl_054','graphics-init.cfg','libcursor_drawing_adapter032','official-arm-sdk-921','native-qca-broker']:
 assert x not in inner and x not in outer,x
assert 'native_fds[5]' in outer and 'entry->d_name[4]>'+"'4'" in inner
print('PASS: commercial original init, four immutable images, isolated fresh data, no SDK library/config substitution, bounded return')
