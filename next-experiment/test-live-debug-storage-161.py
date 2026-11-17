"""Check stage attribution and privacy without requiring mount privileges."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class StorageStages(unittest.TestCase):
    def test_separate_failure_stages_and_no_secret_output(self):
        with tempfile.TemporaryDirectory(prefix='storage161-') as directory:
            root = Path(directory)
            (root / 'empty').write_bytes(b'')
            (root / 'nonempty').write_bytes(b'synthetic-log-never-export')
            (root / 'key').write_bytes(b'synthetic-key-never-export')
            (root / 'key').chmod(0o600)
            (root / 'link').symlink_to(root / 'empty')
            source = '#define _GNU_SOURCE\n#include "' + str(BASE / 'live-debug-storage-161.h') + '"\n'
            source += r'''
int main(int argc,char **argv) {
 if(argc!=7)return 1;
 int fd=open(argv[1],O_RDONLY | O_CLOEXEC);
 if(fd<0)return 2;
 if(live_storage161_bind(-1,argv[1],1)!=-1)return 3;
 int pipes[2];if(pipe(pipes))return 4;
 if(live_storage161_bind(pipes[0],argv[1],1)!=-1)return 5;
 close(pipes[0]);close(pipes[1]);
 if(live_storage161_bind(fd,argv[6],2)!=-1)return 6;
 if(live_storage161_bind(fd,argv[2],2)!=-1)return 7;
 if(live_storage161_bind(fd,argv[3],2)!=-1)return 8;
 if(live_storage161_key(argv[6],argv[5])!=-1)return 9;
 if(live_storage161_key(argv[4],argv[5])!=-1)return 10;
 close(fd);
 return 0;
}
'''
            (root / 'test.c').write_text(source)
            built = subprocess.run(['cc','-Os','-Wall','-Wextra','-Werror',str(root / 'test.c'),'-o',str(root / 'test')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            result = subprocess.run([str(root / 'test'),str(root / 'empty'),str(root / 'nonempty'),str(root / 'link'),
                str(root / 'key'),str(root / 'output'),str(root / 'absent')],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            stages = re.findall(r'^LIVE161_STORAGE_REFUSED item=(\d+) stage=(\d+) errno=(\d+)$',result.stdout,re.M)
            self.assertEqual([(int(item),int(stage)) for item,stage,_ in stages],[(1,1),(1,2),(2,3),(2,4),(2,4),(3,9),(3,11)])
            self.assertTrue(all(int(error)>0 for _,_,error in stages))
            self.assertNotIn('synthetic-',result.stdout + result.stderr)
            self.assertNotIn(str(root),result.stdout + result.stderr)
            self.assertFalse((root / 'output').exists())


if __name__ == '__main__':
    unittest.main()
