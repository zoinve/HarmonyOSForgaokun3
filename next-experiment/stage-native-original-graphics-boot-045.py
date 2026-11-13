"""Inert staging only, with independent capture-only archive validation."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('stage-native-original-graphics-boot-044.py')))['source']
for old, new in [('native-original-graphics-boot-044', 'native-original-graphics-boot-045'),
                 ('native-presentation-package-044-independent', 'native-presentation-package-045-independent'),
                 ('1c4aa6a12e636430f7892a709fd60ef1fd133df4bb55ac3ea0624d1b3c3d29d1', '18d21887be15c02d15dde6b4fcaf8250e0dba1b755fcec3abd7a9c2511909d09'),
                 ('bootstrap_source_changes_only_original_mnt_restore', 'bootstrap_source_changes_only_incremental_perf_capture')]:
    assert old in source, old
    source = source.replace(old, new)
compile(source, 'inert-native045-stage', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'inert-native045-stage', 'exec'), {'__name__': '__main__', '__file__': __file__})
