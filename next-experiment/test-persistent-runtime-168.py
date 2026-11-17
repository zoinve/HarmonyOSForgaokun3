from pathlib import Path
import runpy
import unittest

BASE=Path(__file__).resolve().parent
generator=runpy.run_path(str(BASE/'build-commercial-native-168.py'))
P=Path('/home/zoinve/harmony-virgl-883/commercial61-native-164')

class MemoryHistoryTests(unittest.TestCase):
    def test_change_only_selects_history_wrapper_and_runtime_path(self):
        old=runpy.run_path(str(BASE/'build-commercial-native-166.py'))
        source=(P/'bootstrap-runtime087.c').read_text()
        expected=old['runtime166'](source).replace('persistent-runtime-166.h','persistent-runtime-168.h').replace('persistent_runtime166();','persistent_runtime168();')
        self.assertEqual(generator['runtime168'](source),expected)
        outer=(P/'init.c').read_text()
        args=('0'*64,'eaa446cb-b02a-494f-8a5e-a02c8516cbc7')
        self.assertEqual(generator['outer168'](outer,*args),old['outer166'](outer,*args).replace('/commercial61-native-166/bootstrap-runtime087','/commercial61-native-168/bootstrap-runtime087'))

    def test_log_is_preserved_before_original_memory_preinit(self):
        header=(BASE/'persistent-runtime-168.h').read_text()
        self.assertIn('#include "persistent-runtime-166.h"',header)
        self.assertIn('persistent_runtime166();',header)
        self.assertIn('renameat(datadir,"commercial-memmgr108.log",history,"commercial-memmgr108.log")',header)
        self.assertIn('AT_SYMLINK_NOFOLLOW',header)
        self.assertIn('syncfs(root)',header)
        for forbidden in ['unlink(', 'truncate(', '/data/app/', '/data/service/']:
            self.assertNotIn(forbidden,header)

if __name__=='__main__':unittest.main()
