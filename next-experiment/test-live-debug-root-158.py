"""Reproduce the absolute /system symlink guard bug without target changes."""
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class RootResolution(unittest.TestCase):
    def test_absolute_links_are_resolved_in_target_root(self):
        with tempfile.TemporaryDirectory(prefix='root158-') as directory:
            root = Path(directory)
            target = root / 'target'
            (target / 'usr/system/bin').mkdir(parents=True)
            (target / 'usr/system/bin/init').write_text('not an executable; path fixture only')
            (target / 'system').symlink_to('/usr/system')
            test = '#define _GNU_SOURCE\n#include "' + str(BASE / 'live-debug-root-158.h') + '"\n#include <sys/stat.h>\n'
            test += r'''
int main(int argc, char **argv) {
 if (argc!=2) return 1;
 int root=open(argv[1],O_PATH|O_DIRECTORY|O_CLOEXEC);
 if(root<0)return 2;
 int naive=openat(root,"system/bin/init",O_PATH|O_CLOEXEC);
 if(naive>=0)return 3;
 int checked=live_root158_open(root,"system/bin/init");
 struct stat metadata;
 if(checked<0 || fstat(checked,&metadata) || !S_ISREG(metadata.st_mode))return 4;
 close(checked);
 if(live_root158_open(root,"/etc/passwd")>=0)return 5;
 if(live_root158_open(root,"../../etc/passwd")>=0)return 6;
 close(root);
 return 0;
}
'''
            (root / 'test.c').write_text(test)
            compiled = subprocess.run(['cc','-Wall','-Wextra','-Werror',str(root / 'test.c'),'-o',str(root / 'test')],capture_output=True,text=True)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            self.assertEqual(subprocess.run([str(root / 'test'),str(target)],timeout=5).returncode,0)


if __name__ == '__main__':
    unittest.main()
