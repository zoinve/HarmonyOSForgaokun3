"""Exercise real sysfs ancestry selection without root or physical media access."""
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
FIXTURE = r'''
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
static int read_text(const char *path, char *text, size_t capacity) {
 int fd=open(path,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
 if(fd<0)return -1;
 ssize_t n=read(fd,text,capacity-1);close(fd);
 if(n<0 || n>=(ssize_t)capacity-1)return -1;
 text[n]=0;return 0;
}
#define USB174_NO_OBSERVER
#include "native-usb-storage-174.h"
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 int dev=open(argv[2],O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 usb174_inventory(argv[1],dev);
 if(dev>=0)close(dev);
 return 0;
}
'''


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='usb-storage174-')
        self.root = Path(self.temp.name)
        source = self.root / 'fixture.c'
        source.write_text(FIXTURE)
        self.binary = self.root / 'fixture'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE), str(source),
                        '-o', str(self.binary)], check=True, capture_output=True, timeout=30)
        self.sys = self.root / 'sys'
        (self.sys / 'class/block').mkdir(parents=True)
        (self.sys / 'bus/usb').mkdir(parents=True)
        (self.sys / 'bus/pci').mkdir()
        self.dev = self.root / 'dev'
        self.dev.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def disk(self, name, usb=True):
        parent = self.sys / 'devices' / ('usb3/3-1' if usb else 'misleading-usb-internal')
        parent.mkdir(parents=True, exist_ok=True)
        if not (parent / 'subsystem').exists():
            (parent / 'subsystem').symlink_to(self.sys / ('bus/usb' if usb else 'bus/pci'))
        (parent / 'idVendor').write_text('346d\n')
        (parent / 'idProduct').write_text('5678\n')
        (parent / 'serial').write_text('PRIVATE_SERIAL_NEVER_EXPORT')
        block = parent / 'host/block' / name
        block.mkdir(parents=True)
        (self.sys / 'class/block' / name).symlink_to(block)
        for attr, value in {'dev':'8:1\n', 'size':'61849600\n', 'ro':'0\n', 'removable':'1\n'}.items():
            (block / attr).write_text(value)
        return block

    def run_inventory(self):
        result = subprocess.run([str(self.binary), str(self.sys), str(self.dev)],
                                check=True, capture_output=True, text=True, timeout=5)
        self.assertNotIn('PRIVATE_SERIAL', result.stdout + result.stderr)
        return result.stdout

    def test_usb_ancestry_and_no_block_node_fabrication(self):
        self.disk('sda')
        self.disk('nvme0n1', usb=False)
        output = self.run_inventory()
        self.assertIn('name=sda vid=346d pid=5678', output)
        self.assertNotIn('name=nvme0n1', output)
        self.assertIn('matching_target_nodes=0 node_scan_complete=1', output)
        self.assertEqual(list(self.dev.iterdir()), [])

    def test_malformed_metadata_and_partial_vid_fail_closed(self):
        block = self.disk('sda')
        (block / 'dev').write_text('8:1 trailing\n')
        self.assertIn('INVENTORY count=0', self.run_inventory())
        (block / 'dev').write_text('8:1\n')
        (block / 'size').write_text('-1\n')
        self.assertIn('INVENTORY count=0', self.run_inventory())
        (block / 'size').write_text('61849600\n')
        (block.parents[2] / 'idVendor').write_text('346dgarbage\n')
        self.assertIn('INVENTORY count=0', self.run_inventory())

    def test_regular_file_or_symlink_is_not_block_node(self):
        self.disk('sda')
        (self.dev / 'sda').write_text('not a block device')
        (self.dev / 'block').symlink_to(self.root)
        output = self.run_inventory()
        self.assertIn('matching_target_nodes=0', output)

    def test_partition_and_optional_fields(self):
        block = self.disk('sda1')
        (block / 'partition').write_text('1\n')
        (block / 'removable').unlink()
        self.assertIn('ro=0 removable=-1 partition=1', self.run_inventory())


if __name__ == '__main__':
    unittest.main()
