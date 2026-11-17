"""Exercise diagnostic history using real temporary files, FIFOs and the old gate."""
from pathlib import Path
import os
import runpy
import stat
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
HARNESS = r'''
#define _GNU_SOURCE
#include <stdio.h>
#include "persistent-diagnostic-history-173.h"
int main(int argc,char **argv) {
 if(argc!=3)return 90;
 int data=open(argv[1],O_RDONLY|O_DIRECTORY|O_NOFOLLOW),history=open(argv[2],O_RDONLY|O_DIRECTORY|O_NOFOLLOW);
 if(data<0 || history<0)return 91;
 unsigned files=0,fifos=0;int result=persistent173_archive(data,history,&files,&fifos);
 close(data);close(history);printf("files=%u fifos=%u\n",files,fifos);return result?1:0;
}
'''

class HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='persistent173-harness-')
        root = Path(cls.temp.name)
        source = root / 'test.c'
        source.write_text(HARNESS)
        cls.binary = root / 'test'
        subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),str(source),'-o',str(cls.binary)],check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def archive(self,data,history):
        return subprocess.run([str(self.binary),str(data),str(history)],capture_output=True,text=True,timeout=5)

    def test_regular_and_fifo_preserved_without_app_data_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, history = root / 'data', root / 'history'
            data.mkdir();history.mkdir()
            log = data / 'commercial-collaboration-ready116.log'
            log.write_bytes(b'old checkpoint\n')
            inode = log.stat().st_ino
            os.mkfifo(data / 'commercial-collaboration-ready116.fifo')
            (data / 'application.db').write_bytes(b'fixture application bytes')
            result = self.archive(data,history)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('files=1 fifos=1',result.stdout)
            self.assertEqual((history / log.name).read_bytes(),b'old checkpoint\n')
            self.assertEqual((history / log.name).stat().st_ino,inode)
            self.assertTrue(stat.S_ISFIFO((history / 'commercial-collaboration-ready116.fifo').stat().st_mode))
            self.assertEqual((data / 'application.db').read_bytes(),b'fixture application bytes')

    def test_symlinks_and_archive_collision_refused(self):
        for case in ['symlink','collision','directory','hardlink','wrong_fifo_type']:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                data, history = root / 'data', root / 'history'
                data.mkdir();history.mkdir()
                log = data / 'commercial-collaboration-ready116.log'
                (root / 'outside').write_bytes(b'unchanged')
                if case == 'symlink':log.symlink_to(root / 'outside')
                elif case == 'directory':log.mkdir()
                elif case == 'hardlink':os.link(root / 'outside',log)
                elif case == 'collision':
                    log.write_bytes(b'current')
                    (history / log.name).write_bytes(b'prior archive')
                else:(data / 'commercial-collaboration-ready116.fifo').write_bytes(b'not a FIFO')
                self.assertNotEqual(self.archive(data,history).returncode,0)
                self.assertEqual((root / 'outside').read_bytes(),b'unchanged')
                if case == 'collision':
                    self.assertEqual(log.read_bytes(),b'current')
                    self.assertEqual((history / log.name).read_bytes(),b'prior archive')

    def test_existing_gate_log_failure_then_fresh_current_event(self):
        fixture = runpy.run_path(str(BASE / 'test-oobe-startup-gate-116.py'))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, history, binary = root / 'data', root / 'history', root / 'bin'
            data.mkdir();history.mkdir();binary.mkdir()
            old = data / 'commercial-collaboration-ready116.log'
            old.write_text('previous boot checkpoint\n')
            os.mkfifo(data / 'commercial-collaboration-ready116.fifo')
            for command in ['cat','seq','sleep','mkfifo','rm','timeout','grep']:
                (binary / command).symlink_to('/usr/bin/' + command)
            for name,text in {'pidof':'#!/bin/sh\nprintf "1080\\n"\n',
                'hilog':'#!/bin/sh\nprintf "%s\\n" "$MOCK_EVENT"\n'}.items():
                path = binary / name
                path.write_text(text);path.chmod(0o755)
            source = fixture['SOURCE'].replace('/system/bin/',str(binary) + '/').replace('/data/',str(data) + '/')
            env = dict(os.environ,MOCK_EVENT=fixture['EVENT'])
            before = subprocess.run(['/bin/sh','-c',source],env=env,capture_output=True,text=True,timeout=5)
            self.assertNotEqual(before.returncode,0)
            self.assertEqual(old.read_text(),'previous boot checkpoint\n')
            self.assertEqual(self.archive(data,history).returncode,0)
            after = subprocess.run(['/bin/sh','-c',source],env=env,capture_output=True,text=True,timeout=5)
            self.assertEqual(after.returncode,0,after.stderr)
            self.assertIn('CFWK116_CHECKPOINT_OBSERVED',old.read_text())
            self.assertEqual((history / old.name).read_text(),'previous boot checkpoint\n')

    def test_complete_runtime_compiles_and_original_services_unchanged(self):
        generator = runpy.run_path(str(BASE / 'build-commercial-native-173.py'))
        original = Path('/home/zoinve/harmony-virgl-883/commercial61-native-164/bootstrap-runtime087.c').read_text()
        source = generator['runtime173'](original)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'runtime.c'
            path.write_text(source)
            proc = subprocess.run(['gcc','-fsyntax-only','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),str(path)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
        for name in ['commercial_graphics016','guest_permissive_config_047','readonly_image']:
            start = original.index('static void ' + name + '(')
            end = original.index('\n}',start) + 2
            self.assertIn(original[start:end],source)
        self.assertIn('execve(arguments[0], arguments, environment);',source)

if __name__ == '__main__':unittest.main()
