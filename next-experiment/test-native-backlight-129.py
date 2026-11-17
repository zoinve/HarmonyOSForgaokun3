"""Verify composer glue and real-sysfs failure propagation without device writes."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parent

class BacklightTests(unittest.TestCase):
    def test_native_entrypoint_contract_and_failures(self):
        with tempfile.TemporaryDirectory(prefix='backlight129-test-') as directory:
            obj=Path(directory)/'backend.o'
            binary=Path(directory)/'test'
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-c',str(BASE/'gaokun-basic-sysfs-001.c'),'-o',str(obj)],check=True)
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pthread',str(BASE/'test-native-backlight-129.cpp'),str(obj),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)

    def test_only_two_original_stubs_are_replaced(self):
        adapt=runpy.run_path(str(BASE/'build-commercial-composer-129.py'))['adapt']
        before='API GetDisplayBacklight(uint32_t, uint32_t *) { native_trace_007("GetDisplayBacklight",0); return UNSUPPORTED; }\nAPI SetDisplayBacklight(uint32_t, uint32_t) { native_trace_007("SetDisplayBacklight",0); return UNSUPPORTED; }'
        result=adapt('before\n'+before+'\nafter')
        self.assertTrue(result.startswith('before\n'))
        self.assertTrue(result.endswith('\nafter'))
        self.assertIn('NativeBacklight129::get(device,level)',result)
        self.assertIn('NativeBacklight129::set(device,level)',result)
        with self.assertRaises(AssertionError):adapt('different ABI')

if __name__=='__main__':unittest.main()
