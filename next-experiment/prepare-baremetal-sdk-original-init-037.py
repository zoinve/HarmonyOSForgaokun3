"""Replace only test /data with fresh RAM-backed ext4; never attach original userdata."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-036.py')))
source=parent['source']
anchor='int main(void)'
assert source.count(anchor)==1
source=source.replace(anchor,'''static void volatile_ext4_data_037(void)
{
    char name[32], path[128], identity[128];
    int selected = 0;
    for (unsigned i = 0; i < 100; ++i) {
        selected = sdk_select_disk_035("/sys/class/block", "sdk-testdata", 1048576, name, sizeof(name));
        if (selected < 0) fail("unsafe scratch data identity");
        if (selected == 1) break;
        usleep(20000);
    }
    if (selected != 1) fail("RAM-backed scratch data not enumerated");
    snprintf(path, sizeof(path), "/sys/class/block/%s/dev", name);
    unsigned major_number, minor_number;
    if (read_path(path, identity, sizeof(identity)) <= 0 ||
        sscanf(identity, "%u:%u", &major_number, &minor_number) != 2) fail("scratch data major/minor");
    snprintf(path, sizeof(path), "/dev/%s", name);
    struct stat st;
    if (lstat(path, &st)) {
        if (errno != ENOENT || mknod(path, S_IFBLK | 0600, makedev(major_number, minor_number)))
            fail("scratch data node");
        if (lstat(path, &st)) fail("scratch data node metadata");
    }
    if (!S_ISBLK(st.st_mode) || st.st_rdev != makedev(major_number, minor_number))
        fail("scratch data node identity");
    int fd = open(path, O_RDWR | O_CLOEXEC), read_only = 1;
    if (fd < 0 || ioctl(fd, BLKROGET, &read_only) || read_only) fail("fresh scratch data writable");
    close(fd);
    if (mount(path, "/data", "ext4", MS_NOSUID | MS_NODEV | MS_NOATIME, "data=ordered"))
        fail("fresh RAM-backed ext4 data");
    dprintf(1, "ORIGINAL_INIT037_DATA device=%s fresh_ext4=1 ram_backed=1 original_userdata_attached=0\\n", name);
}

'''+anchor)
anchor='    if (mount("tmpfs", "/data", "tmpfs", MS_NOSUID | MS_NODEV, "mode=0755,size=256m")) fail("volatile data only");'
assert source.count(anchor)==1;source=source.replace(anchor,'    volatile_ext4_data_037();')
source=source.replace('ORIGINAL_INIT036_','ORIGINAL_INIT037_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-036','baremetal-sdk-original-init-037')
compile(payload,'original-init-037-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
