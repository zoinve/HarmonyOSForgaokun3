"""New counted 044 entry only, with fresh inventory and unchanged 64 MiB reserve."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('install-native-presentation-043-attempt-002.py')))
artifact_table = parent['artifact_table']
source = parent['source']
for old, new in [
    ('native-original-graphics-043', 'native-original-graphics-044'),
    ('native-original-graphics-boot-043', 'native-original-graphics-boot-044'),
    ('efi-install-043', 'efi-install-044'),
    ('title HarmonyOS 043', 'title HarmonyOS 044'),
    ('native-presentation-043-installation.json', 'native-presentation-044-installation.json'),
    ('native-presentation-043-efi-archive-022.json', 'native-presentation-044-efi-inventory.json'),
    ('native-presentation-package-043-independent', 'native-presentation-package-044-independent'),
    ('345590', '699477'),
    ('b2a0581f8869ca1d5fb6ee62bd1d0b1866c32832c73d811411f53a6f076fa3f7', '1c4aa6a12e636430f7892a709fd60ef1fd133df4bb55ac3ea0624d1b3c3d29d1'),
    ("retired['efi_files_after']", "retired['files']"),
    ("retired['configs_after']", "retired['configs']"),
]:
    assert old in source, old
    source = source.replace(old, new)
anchor = "    assert audited['archive_metadata_preserved'] and audited['original_images_independent_hashes']"
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + "\n    assert audited['bootstrap_source_changes_only_original_mnt_restore']\n    assert audited['overlay_members_verified']==['init','native-target/bootstrap','native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so']")
compile(source, 'install-native044', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'install-native044', 'exec'))
