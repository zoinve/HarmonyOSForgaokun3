"""Prove reopened log identity and refusal of wrong paths, symlinks and inodes."""
from pathlib import Path
import json
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parent


class LogIdentity(unittest.TestCase):
    def test_same_inode_readonly_and_fail_closed_paths(self):
        with tempfile.TemporaryDirectory(prefix='log163-') as directory:
            root=Path(directory)
            (root/'other').mkdir()
            for name in ['interactive-hilog030.log','native.log','other/interactive-hilog030.log']:
                (root/name).write_bytes(b'synthetic-content-not-for-output')
            (root/'linked').symlink_to(root/'other',target_is_directory=True)
            source='#define _GNU_SOURCE\n#include <unistd.h>\n#include <string.h>\n'
            source+='static const char *forced_path;\nstatic ssize_t fixture_readlink(const char*,char*,size_t);\n#define readlink fixture_readlink\n'
            source+='#define LIVE163_HILOG_PREFIX '+json.dumps(str(root)+'/')+'\n'
            source+='#define LIVE163_NATIVE_PATH '+json.dumps(str(root/'native.log'))+'\n'
            source+='#include "'+str(BASE/'live-debug-log-163.h')+'"\n#undef readlink\n'
            source+=r'''
static ssize_t fixture_readlink(const char *reference,char *output,size_t size) {
 if(!forced_path)return readlink(reference,output,size);
 size_t length=strlen(forced_path);if(length>size)length=size;
 memcpy(output,forced_path,length);return (ssize_t)length;
}
int main(int argc,char **argv) {
 if(argc!=5)return 1;
 int fd=open(argv[1],O_RDONLY | O_CLOEXEC);if(fd<0)return 2;
 int reopened=live_log163_reopen(fd,1);
 struct stat old,current;
 if(reopened<0 || fstat(fd,&old) || fstat(reopened,&current) || old.st_dev!=current.st_dev || old.st_ino!=current.st_ino)return 3;
 if((fcntl(reopened,F_GETFL)&O_ACCMODE)!=O_RDONLY)return 4;
 close(reopened);
 if(live_log163_reopen(-1,1)!=-1 || errno!=EBADF)return 5;
 int pipes[2];if(pipe(pipes))return 6;
 if(live_log163_reopen(pipes[0],1)!=-1 || errno!=EINVAL)return 7;
 close(pipes[0]);close(pipes[1]);
 if(live_log163_reopen(fd,2)!=-1 || errno!=EINVAL)return 8;
 forced_path=argv[2];
 if(live_log163_reopen(fd,1)!=-1 || errno!=ESTALE)return 9;
 forced_path=argv[3];
 if(live_log163_reopen(fd,1)!=-1 || errno!=ELOOP)return 10;
 forced_path=NULL;close(fd);
 fd=open(argv[4],O_RDONLY | O_CLOEXEC);
 if(fd<0)return 11;
 reopened=live_log163_reopen(fd,2);
 if(reopened<0)return 12;
 close(reopened);close(fd);
 if(live_log163_path("/outside/interactive-hilog030.log",1) || live_log163_path(argv[1],7))return 13;
 return 0;
}
'''
            (root/'test.c').write_text(source)
            built=subprocess.run(['cc','-Os','-Wall','-Wextra','-Werror',str(root/'test.c'),'-o',str(root/'test')],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            done=subprocess.run([str(root/'test'),str(root/'interactive-hilog030.log'),str(root/'other/interactive-hilog030.log'),
                str(root/'linked/interactive-hilog030.log'),str(root/'native.log')],capture_output=True,text=True,timeout=5)
            self.assertEqual(done.returncode,0,done.stdout+done.stderr)
            self.assertIn('stage=9',done.stdout)
            self.assertIn('stage=7',done.stdout)
            self.assertNotIn('synthetic-content',done.stdout+done.stderr)
            self.assertNotIn(str(root),done.stdout+done.stderr)


if __name__=='__main__':
    unittest.main()
