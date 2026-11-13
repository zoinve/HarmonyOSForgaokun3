"""Restore the genuine init_early /mnt tmpfs, not a sandbox bypass."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-093.py')))
source = parent['source'].replace('ORIGINAL_INIT093_', 'ORIGINAL_INIT094_').replace('GRAPHICS093_', 'GRAPHICS094_')
assert source.count('#include <sys/statvfs.h>') == 1
source = source.replace('#include <sys/statvfs.h>', '#include <sys/statvfs.h>\n#include <sys/vfs.h>')
helpers = r'''
/* Original init_early SHA 9b475fa2588d4a7f46995de26d61689ce1bb8f1b7ce2c4588fac00c244c94824:
   mount calls 0x23500 and 0x23520; strings tmpfs, /mnt, mode=0755. */
static void graphics_runtime_mnt_094(void)
{
    _Static_assert(MS_NOSUID == 2, "original early mount flags");
    _Static_assert(MS_SLAVE == 0x80000, "original early propagation flags");
    directory("/mnt", 0755);
    struct stat node;
    if (lstat("/mnt", &node) || !S_ISDIR(node.st_mode)) fail("runtime mnt directory");
    if (mount("tmpfs", "/mnt", "tmpfs", MS_NOSUID, "mode=0755")) fail("original early mnt tmpfs");
    if (mount(NULL, "/mnt", NULL, MS_SLAVE, NULL)) fail("original early mnt slave propagation");
    struct statfs fs;
    struct statvfs sv;
    if (statfs("/mnt", &fs) || statvfs("/mnt", &sv) || stat("/mnt", &node) ||
        (unsigned long)fs.f_type != 0x01021994UL || (sv.f_flag & ST_RDONLY) ||
        !(sv.f_flag & ST_NOSUID) || (node.st_mode & 07777) != 0755 || node.st_uid || node.st_gid)
        fail("original early mnt mount verification");
    dprintf(1, "GRAPHICS094_MNT_RUNTIME type=%lx flags=%lu mode=%o uid=%u gid=%u propagation_slave=1 original_early_calls=23500,23520\n",
            (unsigned long)fs.f_type, (unsigned long)sv.f_flag, (unsigned)(node.st_mode & 07777),
            (unsigned)node.st_uid, (unsigned)node.st_gid);
}

static void graphics_mount_state_094(unsigned sample)
{
    const char *paths[] = {"/", "/mnt"};
    for (unsigned k = 0; k < 2; ++k) {
        struct statvfs st;
        int rc = statvfs(paths[k], &st);
        int saved = errno;
        dprintf(1, "GRAPHICS094_MOUNT_STATE sample=%u path=%s stat=%d errno=%d flags=%lu\n",
                sample, paths[k], rc, rc ? saved : 0, rc ? 0UL : (unsigned long)st.f_flag);
    }
}
'''
anchor = 'static void graphics_foundation_query_078('
assert source.count(anchor) == 1
source = source.replace(anchor, helpers + '\n' + anchor)
anchor = '    graphics_ashmem_074();'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n    graphics_runtime_mnt_094();')
start = source.index('static void graphics_account_query_090(')
body = source.index('{', start)
source = source[:body + 1] + '\n    graphics_mount_state_094(sample);' + source[body + 1:]
guard = '''from pathlib import Path
import hashlib
assert hashlib.sha256(Path('/home/zoinve/harmony-virgl-883/baremetal-sdk-init-bootstrap-002/init_early.elf').read_bytes()).hexdigest() == '9b475fa2588d4a7f46995de26d61689ce1bb8f1b7ce2c4588fac00c244c94824'
'''
payload = 'source=' + repr(source) + '\n' + guard + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-093', 'baremetal-sdk-original-init-094')
compile(payload, 'original-runtime-mnt-094-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
