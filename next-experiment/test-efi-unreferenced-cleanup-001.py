"""Offline deletion-scope tests; never contacts or modifies the device."""
from pathlib import Path
import runpy
import unittest

class Scope(unittest.TestCase):
    def test_only_unreferenced_known_experiment_artifacts(self):
        choose = runpy.run_path(str(Path(__file__).with_name('cleanup-efi-unreferenced-001.py')))['candidate_paths']
        files = {name: 123 for name in [
            'native-original-graphics-023/initrd.img',
            'native-original-graphics-044/return-overlay.img',
            'native-original-graphics-031/initrd.img',
            'native-original-graphics-031/linux',
            'native-original-graphics-032/initrd.img',
            'native-original-graphics-023/unknown-user-file',
            'commercial61-native-020/initrd.img',
            'EFI/BOOT/BOOTAA64.EFI', 'loader/random-seed',
            'firmware/qcom/test.mbn', 'ubuntu/initrd.img']}
        config = {'loader/entries/manual.conf':
                  'linux \\NATIVE-ORIGINAL-GRAPHICS-031\\linux\ninitrd /native-original-graphics-032/initrd.img\n'}
        self.assertEqual(choose(files, config), [
            'native-original-graphics-023/initrd.img',
            'native-original-graphics-044/return-overlay.img'])

if __name__ == '__main__': unittest.main()
