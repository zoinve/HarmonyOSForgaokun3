"""Exercise real BusyBox hashing/copy/exec with explicit synthetic fixture payload."""
from pathlib import Path
import hashlib
import os
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
loader = runpy.run_path(str(BASE / 'build-commercial-native-161.py'))['loader161']


class Loader(unittest.TestCase):
    def test_hash_fd_and_exclusive_destination_guards(self):
        with tempfile.TemporaryDirectory(prefix='loader161-') as directory:
            root = Path(directory)
            # A host test payload, not a simulated HarmonyOS helper or service.
            (root / 'probe.c').write_text('#include <fcntl.h>\nint main(void){return fcntl(196,F_GETFD)<0 || fcntl(197,F_GETFD)<0 ? 23 : 0;}\n')
            built = subprocess.run(['cc',str(root / 'probe.c'),'-o',str(root / 'probe')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            digest = hashlib.sha256((root / 'probe').read_bytes()).hexdigest()
            script = root / 'loader'
            script.write_text(loader(digest,str(root / 'probe'),str(root / 'copy')))
            def invoke(arguments, descriptors=False):
                command = ['/bin/busybox','sh',str(script),*arguments]
                if not descriptors:
                    return subprocess.run(command,capture_output=True,text=True,timeout=5)
                fd = os.open(root / 'fixture-log',os.O_RDWR | os.O_CREAT,0o600)
                saved = {}
                try:
                    for number in [196,197]:
                        try: saved[number] = os.dup(number)
                        except OSError: saved[number] = None
                        os.dup2(fd,number,inheritable=True)
                    return subprocess.run(command,pass_fds=(196,197),capture_output=True,text=True,timeout=5)
                finally:
                    os.close(fd)
                    for number,previous in saved.items():
                        if previous is None: os.close(number)
                        else: os.dup2(previous,number);os.close(previous)
            self.assertEqual(invoke([]).returncode,77)
            self.assertEqual(invoke(['--native-live159','1;id']).returncode,77)
            self.assertEqual(invoke(['--native-live159','123']).returncode,104)
            first = invoke(['--native-live159','123'],True)
            self.assertEqual(first.returncode,0,first.stdout + first.stderr)
            self.assertIn('ram_hash_verified=1',first.stdout)
            self.assertEqual((root / 'copy').stat().st_mode & 0o777,0o500)
            self.assertEqual(invoke(['--native-live159','123'],True).returncode,106)
            (root / 'copy').unlink()
            (root / 'probe').write_bytes(b'changed synthetic payload')
            self.assertEqual(invoke(['--native-live159','123'],True).returncode,107)
            self.assertFalse((root / 'copy').exists())


if __name__ == '__main__':
    unittest.main()
