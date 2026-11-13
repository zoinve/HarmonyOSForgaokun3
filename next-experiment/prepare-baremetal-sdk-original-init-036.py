"""Match original init_early's /dev tmpfs, populated with real kernel device numbers."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-035.py')))
source=parent['source']
anchor='    int console = open("/dev/console", O_RDWR | O_CLOEXEC);'
assert source.count(anchor)==1
source=source.replace(anchor,'''    /* Original init_early mounts tmpfs at /dev (mount call 0x234d8).
       Snapshot real devtmpfs nodes before replacing this fixture mount. */
    struct kernel_node { char name[256]; mode_t mode; dev_t device; uid_t uid; gid_t gid; };
    static struct kernel_node nodes[256];
    unsigned count = 0;
    DIR *devices = opendir("/dev");
    if (!devices) fail("kernel device directory");
    struct dirent *entry;
    while ((entry = readdir(devices))) {
        if (entry->d_name[0] == '.') continue;
        char path[512];
        snprintf(path, sizeof(path), "/dev/%s", entry->d_name);
        struct stat st;
        if (lstat(path, &st)) fail("kernel device metadata");
        if (!S_ISCHR(st.st_mode) && !S_ISBLK(st.st_mode)) continue;
        if (count == 256) fail("bounded kernel device inventory");
        strcpy(nodes[count].name, entry->d_name);
        nodes[count].mode = st.st_mode;
        nodes[count].device = st.st_rdev;
        nodes[count].uid = st.st_uid;
        nodes[count++].gid = st.st_gid;
    }
    closedir(devices);
    if (umount("/dev") || mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=0755"))
        fail("original early-init tmpfs device filesystem");
    for (unsigned i = 0; i < count; ++i) {
        char path[512];
        snprintf(path, sizeof(path), "/dev/%.255s", nodes[i].name);
        if (mknod(path, nodes[i].mode, nodes[i].device) ||
            chmod(path, nodes[i].mode & 07777) || chown(path, nodes[i].uid, nodes[i].gid))
            fail("genuine kernel-backed tmpfs device node");
    }
'''+anchor)
source=source.replace('ORIGINAL_INIT035_','ORIGINAL_INIT036_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-035','baremetal-sdk-original-init-036')
compile(payload,'original-init-036-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
