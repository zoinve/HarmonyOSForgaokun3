"""Check storage transformation, original-service invariants and compiled headers."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parent
M=runpy.run_path(str(BASE/'build-commercial-native-166.py'))
P=Path('/home/zoinve/harmony-virgl-883/commercial61-native-164')

class PersistentTests(unittest.TestCase):
    def test_outer_removes_all_seed_reset_and_ram_resize(self):
        original=(P/'init.c').read_text()
        changed=M['outer166'](original,'0'*64,'eaa446cb-b02a-494f-8a5e-a02c8516cbc7')
        self.assertNotIn('char *seed123[]',changed)
        self.assertNotIn('ftruncate(ram,8589934592ULL)',changed)
        self.assertNotIn('native_loop(3,"/native-target/scratch-data.ext4"',changed)
        self.assertIn('if(okay && persistent166_prepare())okay=0;',changed)
        self.assertIn('persistent166_finish();',changed)
        for name in ['network083_command','native_child','native_diagnostics']:
            # Every existing native call still exists, not a mocked service path.
            self.assertIn(name,changed)
        self.assertIn('"ext4",MS_RDONLY|MS_NODEV|MS_NOSUID|MS_NOEXEC, "noload"',changed)
        self.assertIn('native_live159_start(child);',changed)

    def test_runtime_scopes_change_to_data_and_handoff_metadata(self):
        source=(P/'bootstrap-runtime087.c').read_text()
        changed=M['runtime166'](source)
        self.assertNotIn('volatile_ext4_data_037',changed)
        self.assertNotIn('genuine online growth',changed)
        self.assertIn('persistent_ext4_data166();',changed)
        self.assertIn('execve(arguments[0], arguments, environment);',changed)
        for name in ['commercial_graphics016','guest_permissive_config_047','readonly_image']:
            before=source.index('static void '+name+'(')
            after=source.index('\n}',before)+2
            self.assertIn(source[before:after],changed)

    def test_headers_do_not_reset_app_data(self):
        outer=(BASE/'persistent-data-166.h').read_text()
        runtime=(BASE/'persistent-runtime-166.h').read_text()
        for forbidden in ['ftruncate(', 'unlink(', 'system(', 'exec', 'chmod(']:
            self.assertNotIn(forbidden,outer+runtime)
        self.assertIn('LOCK_EX|LOCK_NB',outer)
        self.assertIn('LOOP_GET_STATUS64',outer)
        self.assertIn('file.st_dev != mounted_stat.st_dev',outer)
        self.assertIn('file.st_nlink != 1',outer)
        self.assertIn('memcmp(super+104,uuid,16)',outer)
        self.assertIn('umount("/native-data166")',outer)
        self.assertIn('renameat(datadir,owned[i],history,owned[i])',runtime)
        self.assertIn('fsync(root) || syncfs(root)',runtime)
        self.assertNotIn('/data/app/',runtime)
        self.assertNotIn('/data/service/',runtime)

    def test_real_runtime_header_compiles_on_host(self):
        source=(P/'bootstrap-runtime087.c').read_text()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'runtime.c'
            path.write_text(M['runtime166'](source))
            proc=subprocess.run(['gcc','-fsyntax-only','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),str(path)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)

if __name__=='__main__':unittest.main()
