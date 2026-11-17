"""Check555 payloads and execute its fixed reader-install recipe in a temp jail."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import re
import runpy
import shutil
import stat
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
WORK=Path('/home/zoinve/harmony-virgl-883/commercial61-native-555')
source=(BASE/'test-share-native-503.py').read_text()
source=source.replace('commercial61-native-502','commercial61-native-555')
source=source.replace('reports/share-supplicant-499','reports/share-supplicant-543')
namespace=dict(__name__='radio556_base',__file__=str(BASE/'test-radio-native-556.base.py'))
exec(compile(source,namespace['__file__'],'exec'),namespace)

class Candidate(namespace['IntegrationTest']):
    def test_new_reader_and_private_probe_are_packaged(self):
        parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
        entries={name:(mode,data) for name,mode,data in parser(gzip.decompress((WORK/'minimal-overlay.img').read_bytes()))}
        record=json.loads((ROOT/'reports/live-radio-reader-553/result.json').read_text())
        mode,data=entries['live-radio551-reader']
        self.assertEqual(mode&0o777,0o555)
        self.assertEqual(hashlib.sha256(data).hexdigest(),record['sha256'])
        self.assertEqual(entries['native-target/compat525'],(0o40700,b''))
        self.assertNotIn(b'update_config=',entries['native-target/share501/p2p.conf'][1])
        init=(WORK/'init.c').read_text()
        self.assertIn('if(i==5 && started083)(void)network083_command(child,"compat-probe")',init)
        self.assertIn('!strcmp(mode,"compat-probe") ? 20',init)

    def test_fixed_install_recipe_checks_payload_and_preserves_authentication(self):
        init=(WORK/'init.c').read_text()
        match=re.search(r'char \*reader551\[\]=\{"/bin/busybox","sh","-c",\s*((?:\s*"(?:\\.|[^"\\])*")+),NULL\};',init)
        self.assertIsNotNone(match)
        literals=re.findall(r'"(?:\\.|[^"\\])*"',match[1])
        recipe=''.join(ast.literal_eval(literal) for literal in literals)
        self.assertNotIn('sshd_config',recipe)
        self.assertNotIn('authorized_keys',recipe)
        self.assertNotIn('host_ed25519',recipe)
        record=json.loads((ROOT/'reports/live-radio-reader-553/result.json').read_text())
        payload=Path(record['binary']).read_bytes()
        for scenario in ['normal','bad-digest','source-symlink','bin-symlink','target-symlink','stale-temp']:
            with self.subTest(scenario=scenario),tempfile.TemporaryDirectory(prefix='live-loader-556-') as directory:
                root=Path(directory)
                source=root/'reader'
                source.write_bytes(payload)
                jail=root/'jail';(jail/'bin').mkdir(parents=True)
                target=jail/'bin/diag';target.write_bytes(b'original-reader-fixture')
                if scenario=='bad-digest':source.write_bytes(b'wrong')
                if scenario=='source-symlink':
                    source.rename(root/'real-reader');source.symlink_to(root/'real-reader')
                if scenario=='bin-symlink':
                    (jail/'bin').rename(jail/'real-bin');(jail/'bin').symlink_to(jail/'real-bin')
                if scenario=='target-symlink':
                    target.rename(jail/'bin/original');target.symlink_to(jail/'bin/original')
                if scenario=='stale-temp':(jail/'bin/diag551').write_bytes(b'preserve-existing')
                local=recipe.replace('/live-radio551-reader',str(source)).replace('/live-debug157-root',str(jail))
                local=local.replace('/bin/busybox',shutil.which('busybox'))
                self.assertNotIn('/live-radio551-reader',local)
                self.assertNotIn('/live-debug157-root',local)
                result=subprocess.run(['/bin/sh','-c',local],capture_output=True,text=True,timeout=10)
                if scenario=='normal':
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertEqual(target.read_bytes(),payload)
                    self.assertEqual(stat.S_IMODE(target.stat().st_mode),0o500)
                else:
                    self.assertNotEqual(result.returncode,0)
                    self.assertEqual(target.read_bytes(),b'original-reader-fixture')
                if scenario=='stale-temp':
                    self.assertEqual((jail/'bin/diag551').read_bytes(),b'preserve-existing')

if __name__ == '__main__':
    unittest.main()
