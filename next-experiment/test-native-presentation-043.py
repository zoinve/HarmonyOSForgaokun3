"""Offline instrumentation checks, never a hardware/FPS experiment."""
from pathlib import Path
import runpy
import subprocess
import unittest

HERE = Path(__file__).parent
BASE = HERE.parent


class PresentationTests(unittest.TestCase):
    def test_build_is_exclusive_and_guards_existing_artifacts(self):
        path = HERE / 'build-native-presentation-043.py'
        self.assertTrue(path.exists(), 'missing independent build-only adapter')
        text = runpy.run_path(str(path))['payload']
        compile(text, '043-build-offline', 'exec')
        self.assertIn('assert not work.exists() and not local.exists()', text)
        self.assertIn('baseline041_unchanged', text)
        self.assertIn('for path, digest in guarded.items()', text)
        self.assertIn('runtime_verified=False', text)
        self.assertIn('installed=False', text)
        self.assertNotIn('ssh ', text)
        self.assertNotIn('modprobe', text)

    def test_instrumentation_round_trip_preserves_pipeline(self):
        path = HERE / 'native-presentation-043.py'
        self.assertTrue(path.exists(), 'missing reversible instrumentation')
        ns = runpy.run_path(str(path))
        original = (BASE / 'reports/native-render-041/composer-trace.cpp').read_text()
        cursor = (BASE / 'reports/native-render-041/native-cursor-composer-041.h').read_text()
        changed, changed_cursor = ns['adapt'](original, cursor)
        self.assertEqual(ns['strip'](changed, changed_cursor), (original, cursor))
        self.assertIn('NativePresent043::completed(sequence, seconds, microseconds)', changed)
        self.assertIn('NativePresent043::begin("client",', changed)
        self.assertIn('NativePresent043::begin("cursor",', changed_cursor)
        self.assertEqual(changed.count('drmModePageFlip('), original.count('drmModePageFlip('))
        self.assertEqual(changed_cursor.count('drmModePageFlip('), cursor.count('drmModePageFlip('))
        self.assertIn('DRM_CAP_TIMESTAMP_MONOTONIC', changed)

    def test_completion_state_never_fakes_a_presentation(self):
        path = HERE / 'native-presentation-043.h'
        self.assertTrue(path.exists(), 'missing actual completion recorder')
        code = r'''
#include "native-presentation-043.h"
#include <cassert>
int main() {
    using namespace NativePresent043;
    errno = EBUSY;
    completed(5, 1, 2); // orphan is not matched to an invented submission
    assert(!pending.active && completed_count == 0 && errno == EBUSY);
    begin("client", 7); failed(-1, EINVAL);
    assert(!pending.active && completed_count == 0 && errno == EBUSY && used == 0);
    begin("client", 8); completed(6, 1, 3);
    assert(!pending.active && completed_count == 1 && errno == EBUSY);
    begin("client", 9); begin("cursor", 10); completed(7, 1, 4);
    assert(!pending.active && completed_count == 1); // ambiguous overlap excluded
    configure_clock(0, 1); assert(timestamp_monotonic == 1 && used == 0);
    configure_clock(-1, 0); assert(timestamp_monotonic == -1);
    flush();
}
'''
        script = """from pathlib import Path
import tempfile, subprocess
with tempfile.TemporaryDirectory(prefix='presentation043-unit-', dir='/home/zoinve/harmony-virgl-883') as d:
 p=Path(d); (p/'test.cpp').write_text(CODE)
 subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-I/mnt/d/lab/HarmonyOSForMatebookego/next-experiment',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
"""
        script = 'CODE=' + repr(code) + '\n' + script
        result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script,
                                text=True, capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
