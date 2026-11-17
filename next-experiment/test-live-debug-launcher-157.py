"""Check numeric admission and fail-closed launcher behavior without target access."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name('live-debug-launcher-157.c')


class Launcher(unittest.TestCase):
    def test_pid_parser(self):
        with tempfile.TemporaryDirectory(prefix='live-launcher157-') as directory:
            root = Path(directory)
            test = '#define main launcher_main157\n#include "' + str(SOURCE) + '"\n#undef main\n'
            test += r'''
int main(void) {
 long n = 0;
 const char *bad[] = {"", "0", "1", "-2", "+2", "02", "2;id", "2147483648", "123\n"};
 for (unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);++i) if (!number157(bad[i],&n)) return 1;
 if (number157("123",&n) || n!=123) return 2;
 return 0;
}
'''
            (root / 'test.c').write_text(test)
            compiled = subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(root / 'test.c'),'-o',str(root / 'test')],capture_output=True,text=True)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            self.assertEqual(subprocess.run([str(root / 'test')],timeout=5).returncode,0)

    def test_host_execution_refuses_without_native_optin(self):
        with tempfile.TemporaryDirectory(prefix='live-launcher157-') as directory:
            binary = Path(directory) / 'launcher'
            subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(SOURCE),'-o',str(binary)],check=True,capture_output=True)
            for args in [[],['--native-live157','123'],['--native-live157','123;id'],['--other','123']]:
                self.assertEqual(subprocess.run([str(binary),*args],timeout=5).returncode,77)


if __name__ == '__main__':
    unittest.main()
