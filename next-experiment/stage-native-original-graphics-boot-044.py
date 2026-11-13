"""Stage only the independently audited 044 package; require real ARM64 refusals."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('stage-native-original-graphics-boot-043.py')))['source']
source = source.replace('native-original-graphics-boot-043', 'native-original-graphics-boot-044')
source = source.replace('native-presentation-package-043-independent', 'native-presentation-package-044-independent')
source = source.replace('b2a0581f8869ca1d5fb6ee62bd1d0b1866c32832c73d811411f53a6f076fa3f7', '1c4aa6a12e636430f7892a709fd60ef1fd133df4bb55ac3ea0624d1b3c3d29d1')
anchor = "    assert audit['installed'] is False and audit['native_boot_attempted'] is False"
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + "\n    assert audit['overlay_members_verified']==['init','native-target/bootstrap','native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so']\n    assert audit['bootstrap_source_changes_only_original_mnt_restore']")
compile(source, 'inert-native044-stage', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'inert-native044-stage', 'exec'), {'__name__': '__main__', '__file__': __file__})
