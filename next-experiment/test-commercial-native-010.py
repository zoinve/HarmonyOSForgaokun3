"""Offline candidate contract; no inference about original-service runtime."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-010.py').is_file(),'missing capacity/teardown repair'
p=runpy.run_path(str(base/'build-commercial-native-010.py'))
assert '8589934592ULL' in p['inner'] and '8589934592ULL' in p['outer']
assert 'commercial_ram_budget010(total010*1024,available010*1024)' in p['outer']
assert p['outer'].index('commercial_ram_budget010(')<p['outer'].index('ftruncate(ram,8589934592ULL)')
assert 'commercial_bounded010(commercial_finish010,NULL,15000)' in p['outer']
assert 'umount2("/mnt/lab",MNT_DETACH)' in p['outer']
assert '\n    sync();\n    reboot(' not in p['outer']
assert 'left033=210' in p['outer'] and 'elapsed033<90' in p['outer']
assert 'commercial61-original-001/' in p['outer']
assert 'commercial61-native-010-%s' in p['outer']
assert 'char *const arguments[]={"/system/bin/init", "--second-stage",NULL};' in p['inner']
assert 'graphics_provider_050' not in p['inner']
print('PASS: 8 GiB capacity guarded before growth; final snapshot/syncfs/detach bounded; original commercial userland retained')
