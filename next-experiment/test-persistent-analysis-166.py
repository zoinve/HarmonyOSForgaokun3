from pathlib import Path
import runpy
import unittest

BASE=Path(__file__).resolve().parent
summarize=runpy.run_path(str(BASE/'analyze-persistent-data-166.py'))['summarize']
BOOT='12345678-1234-1234-1234-123456789abc'
PREV='87654321-1234-1234-1234-123456789abc'
TEXT='''PERSISTENT166_READY nvme_backed=1 capacity=8589934592 seed_copied=0 inode_verified=1 exclusive_lock=1
NATIVE_LOOP index=3 readonly=0 bytes=8589934592 ram_data=0
PERSISTENT166_RUNTIME disk_backed=1 seed_reset=0 boot=BOOT previous_present=0 previous=none archived=0
42 41 7:3 / /data rw,nosuid,nodev,noatime - ext4 /dev/loop3 rw,data=ordered
COMMERCIAL001_HANDOFF readonly_images=4 volatile_data=0 persistent_data=1
PERSISTENT166_FLUSHED inner_syncfs=1 inner_unmounted=1 backing_fsync=1 outer_syncfs=1
PERSISTENT166_FINISH status=0 clean_shutdown_not_inferred=0
'''.replace('BOOT',BOOT)

class AnalysisTests(unittest.TestCase):
    def test_first_boot_requires_every_layer(self):
        self.assertTrue(summarize(TEXT,BOOT)['native_disk_mount_and_flush_verified'])
        for line in TEXT.splitlines(True):
            self.assertFalse(summarize(TEXT.replace(line,'',1),BOOT)['native_disk_mount_and_flush_verified'],line)
        for bad in ['PERSISTENT166_REFUSED x\n','OOBE123_SEED_VERIFIED\n','NATIVE_ORIGINAL001_FAIL x\n']:
            self.assertFalse(summarize(TEXT+bad,BOOT)['native_disk_mount_and_flush_verified'])

    def test_second_boot_requires_previous_distinct_boot_and_archived_objects(self):
        second=TEXT.replace('previous_present=0 previous=none archived=0','previous_present=1 previous='+PREV+' archived=5')
        self.assertTrue(summarize(second,BOOT,PREV)['native_disk_mount_and_flush_verified'])
        self.assertFalse(summarize(second,BOOT,BOOT)['native_disk_mount_and_flush_verified'])
        self.assertFalse(summarize(second.replace('archived=5','archived=0'),BOOT,PREV)['native_disk_mount_and_flush_verified'])
        self.assertFalse(summarize(second,BOOT)['native_disk_mount_and_flush_verified'])

if __name__=='__main__':unittest.main()
