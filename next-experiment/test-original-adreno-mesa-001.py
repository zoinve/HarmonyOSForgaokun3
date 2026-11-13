"""Offline build-only gates for the real OHOS Freedreno/MSM backend."""
from pathlib import Path
import runpy
import unittest


class AdrenoBuildTests(unittest.TestCase):
    def test_isolated_original_toolchain_no_install_or_device_access(self):
        p = Path(__file__).with_name('build-original-adreno-mesa-001.py')
        self.assertTrue(p.exists(), 'missing isolated Adreno build')
        s = runpy.run_path(str(p))['payload']
        compile(s, 'adreno001-offline', 'exec')
        for required in ('original-adreno-mesa-001', 'toolchain/ohos-cross.ini',
                         '--wrap-mode=nodownload', '-Dgallium-drivers=freedreno',
                         '-Dfreedreno-kmds=msm', '-Dallow-kcmp=enabled',
                         "['freedreno']", "['msm']", "'device_accessed': False",
                         "'driver_runtime_verified': False", "'installed': False"):
            self.assertIn(required, s)
        self.assertIn('assert all(digest(Path(p))==h for p,h in before.items())', s)
        self.assertIn('libc.so.6', s)
        self.assertNotIn('meson install', s)
        self.assertNotIn('ninja install', s)
        self.assertNotIn('ssh ', s)
        self.assertNotIn('insmod', s)
        self.assertNotIn('/dev/dri/', s)

    def test_clang_compatibility_retains_narrowing_warnings_without_editing_sources(self):
        p = Path(__file__).with_name('build-original-adreno-mesa-002.py')
        self.assertTrue(p.exists(), 'missing fresh compiler-compatibility build')
        s = runpy.run_path(str(p))['payload']
        compile(s, 'adreno002-offline', 'exec')
        self.assertIn('-Wno-error=c++11-narrowing', s)
        self.assertNotIn('-Wno-c++11-narrowing', s)
        self.assertNotIn('original-adreno-mesa-001', s)
        self.assertIn("if key == 'cpp_args':", s)
        self.assertIn("'device_accessed': False", s)
        self.assertIn('assert all(digest(Path(p))==h for p,h in before.items())', s)


if __name__ == '__main__':
    unittest.main()
