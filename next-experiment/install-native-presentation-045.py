"""Install only a new counted entry; preserve the 64 MiB ESP reserve."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('install-native-presentation-044.py')))['source']
for old, new in [('native-original-graphics-044', 'native-original-graphics-045'),
                 ('native-original-graphics-boot-044', 'native-original-graphics-boot-045'),
                 ('efi-install-044', 'efi-install-045'),
                 ('title HarmonyOS 044', 'title HarmonyOS 045'),
                 ('native-presentation-044-installation.json', 'native-presentation-045-installation.json'),
                 ('native-presentation-044-efi-inventory.json', 'native-presentation-045-efi-inventory.json'),
                 ('native-presentation-package-044-independent', 'native-presentation-package-045-independent'),
                 ('699477', '701039'),
                 ('1c4aa6a12e636430f7892a709fd60ef1fd133df4bb55ac3ea0624d1b3c3d29d1', '18d21887be15c02d15dde6b4fcaf8250e0dba1b755fcec3abd7a9c2511909d09'),
                 ('bootstrap_source_changes_only_original_mnt_restore', 'bootstrap_source_changes_only_incremental_perf_capture')]:
    assert old in source, old
    source = source.replace(old, new)
compile(source, 'install-native045', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'install-native045', 'exec'))
