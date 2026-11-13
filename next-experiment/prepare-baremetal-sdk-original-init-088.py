"""Use the genuine readonly system tree at a canonical /system mountpoint."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-087.py')))
source = parent['source'].replace('ORIGINAL_INIT087_', 'ORIGINAL_INIT088_').replace('GRAPHICS087_', 'GRAPHICS088_')
source = source.replace('graphics_profile_events_087', 'graphics_profile_events_088')
source = source.replace('graphics_audit_copy_087', 'graphics_audit_copy_088')
source = source.replace('graphics-audit-087.log', 'graphics-audit-088.log')
old = '    if (symlink("/usr/system", "/system") || symlink("/system/etc", "/etc") ||'
assert source.count(old) == 1
source = source.replace(old, r'''    if (mkdir("/system", 0755) && errno != EEXIST) fail("original system mountpoint");
    struct stat system_st;
    if (lstat("/system", &system_st) || !S_ISDIR(system_st.st_mode))
        fail("original system requires genuine directory");
    if (mount("/usr/system", "/system", NULL, MS_BIND, NULL) ||
        mount(NULL, "/system", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY, NULL))
        fail("original system readonly bind");
    char system_real[4096];
    if (!realpath("/system", system_real) || strcmp(system_real, "/system"))
        fail("original system canonical mountpoint");
    dprintf(1, "GRAPHICS088_SYSTEM_BIND source=/usr/system target=/system canonical=%s readonly=1 original_files=1\n", system_real);
    if (symlink("/system/etc", "/etc") ||''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-087', 'baremetal-sdk-original-init-088')
compile(payload, 'original-system-bind-088-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
