"""Build-only: restore genuine early /mnt tmpfs, retaining original app sandboxes."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('build-native-original-graphics-boot-043.py')))
old_inner = parent['inner']
HEADER = '#include <sys/stat.h>\n#include <sys/statvfs.h>\n#include <sys/vfs.h>'
ANCHOR = '    directory("/mnt",0755);directory("/mnt/sandbox",0755);'
HELPER = r'''
/* Genuine init_early 9b475fa2588d4a7f46995de26d61689ce1bb8f1b7ce2c4588fac00c244c94824:
   mount calls 0x23500 (tmpfs, /mnt, MS_NOSUID, mode=0755) and 0x23520 (MS_SLAVE). */
static void native_runtime_mnt044(void)
{
    _Static_assert(MS_NOSUID == 2, "original mount flags");
    _Static_assert(MS_SLAVE == 0x80000, "original propagation flags");
    directory("/mnt", 0755);
    struct stat st;
    if (lstat("/mnt", &st) || !S_ISDIR(st.st_mode)) fail("original runtime mnt directory");
    if (mount("tmpfs", "/mnt", "tmpfs", MS_NOSUID, "mode=0755")) fail("original runtime mnt tmpfs");
    if (mount(NULL, "/mnt", NULL, MS_SLAVE, NULL)) fail("original runtime mnt propagation");
    struct statfs fs;
    struct statvfs sv;
    if (statfs("/mnt", &fs) || statvfs("/mnt", &sv) || stat("/mnt", &st) ||
        (unsigned long)fs.f_type != 0x01021994UL || (sv.f_flag & ST_RDONLY) ||
        !(sv.f_flag & ST_NOSUID) || (st.st_mode & 07777) != 0755 || st.st_uid || st.st_gid)
        fail("original runtime mnt verification");
    dprintf(1, "NATIVE_MNT044_READY type=%lx flags=%lu mode=%o uid=%u gid=%u slave=1 original_early_calls=23500,23520\n",
            (unsigned long)fs.f_type, (unsigned long)sv.f_flag, (unsigned)(st.st_mode & 07777),
            (unsigned)st.st_uid, (unsigned)st.st_gid);
}
'''
assert old_inner.count('#include <sys/stat.h>') == old_inner.count(ANCHOR) == 1
assert old_inner.count('int main(void)\n{') == 1
inner = old_inner.replace('#include <sys/stat.h>', HEADER)
inner = inner.replace('int main(void)\n{', HELPER + '\nint main(void)\n{')
inner = inner.replace(ANCHOR, '    native_runtime_mnt044();\n' + ANCHOR)


def restore_inner(source):
    assert source.count(HELPER + '\n') == 1
    assert source.count('    native_runtime_mnt044();\n' + ANCHOR) == 1
    assert source.count(HEADER) == 1
    return source.replace(HELPER + '\n', '', 1).replace('    native_runtime_mnt044();\n' + ANCHOR, ANCHOR, 1).replace(HEADER, '#include <sys/stat.h>', 1)


assert restore_inner(inner) == old_inner
frozen = Path(__file__).resolve().parents[1] / 'reports/native-original-graphics-boot-043'
assert (frozen / 'bootstrap.c').read_bytes() == old_inner.encode()
assert (frozen / 'init.c').read_bytes() == parent['outer'].encode()
outer = parent['outer'].replace('native-interactive-043-%s', 'native-interactive-044-%s').replace('NATIVE_UNATTENDED043', 'NATIVE_UNATTENDED044')
marker = '\n# A streaming, independent complete-archive comparison'
assert parent['payload'].count(marker) == 1
body, tail = parent['payload'].split(marker, 1)
assert body.count('inner=' + repr(old_inner)) == body.count('outer=' + repr(parent['outer'])) == 1
body = body.replace('inner=' + repr(old_inner), 'inner=' + repr(inner), 1)
body = body.replace('outer=' + repr(parent['outer']), 'outer=' + repr(outer), 1)
body = body.replace('native-original-graphics-boot-043', 'native-original-graphics-boot-044')
body = body.replace("original_work=Path('/home/zoinve/harmony-virgl-883/native-original-graphics-boot-041')",
                    "original_work=Path('/home/zoinve/harmony-virgl-883/native-original-graphics-boot-043')")
guard = '''from pathlib import Path
import hashlib
assert hashlib.sha256(Path('/home/zoinve/harmony-virgl-883/baremetal-sdk-init-bootstrap-002/init_early.elf').read_bytes()).hexdigest()=='9b475fa2588d4a7f46995de26d61689ce1bb8f1b7ce2c4588fac00c244c94824'
'''
tail = marker + tail
assert tail.count("keep={'init',vdi}") == 1
tail = tail.replace("keep={'init',vdi}", "bootstrap_name='native-target/bootstrap'\nkeep={'init',vdi,bootstrap_name}")
tail = tail.replace("assert set(changed)=={'init',vdi,scratch_name}", "assert set(changed)=={'init',bootstrap_name,scratch_name}")
tail = tail.replace("for name in ['init',vdi]", "for name in ['init',bootstrap_name,vdi]")
for old, new in [('changed_vs041', 'changed_vs043'), ('baseline041_files', 'baseline043_files'), ('preserved_vs041', 'preserved_vs043')]:
    tail = tail.replace(old, new)
payload = guard + body + tail
compile(payload, 'native-original-mnt-044-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)
