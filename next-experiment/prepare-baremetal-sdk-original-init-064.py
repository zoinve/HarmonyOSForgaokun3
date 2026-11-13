"""Passive actual DRM DAC and service-group observations, without permission edits."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-063.py')))
source = parent['source'].replace('ORIGINAL_INIT063_', 'ORIGINAL_INIT064_').replace('GRAPHICS063_', 'GRAPHICS064_')
anchor = '        long rs_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
        const char *drm_paths[] = {"/dev/dri/card0", "/dev/dri/renderD128"};
        for (unsigned k = 0; k < 2; ++k) {
            struct stat st;
            int rc = stat(drm_paths[k], &st);
            dprintf(1, "GRAPHICS064_DRM_PERMISSIONS sample=%u path=%s stat=%d uid=%u gid=%u mode=%o\\n",
                    sample, drm_paths[k], rc, rc ? 0 : (unsigned)st.st_uid,
                    rc ? 0 : (unsigned)st.st_gid, rc ? 0 : (unsigned)(st.st_mode & 07777));
        }''')
anchor = '''                if (read_path(path, text, sizeof(text)) > 0) {
                    char *uid = strstr(text, "Uid:");'''
assert source.count(anchor) == 1
source = source.replace(anchor, '''                if (read_path(path, text, sizeof(text)) > 0) {
                    const char *keys[] = {"Gid:", "Groups:"};
                    for (unsigned k = 0; k < 2; ++k) {
                        const char *value = strstr(text, keys[k]);
                        if (!value) continue;
                        const char *end = strchr(value, '\\n');
                        if (!end) end = value + strlen(value);
                        dprintf(1, "GRAPHICS064_CREDENTIAL pid=%ld %.*s\\n", pid, (int)(end-value), value);
                    }
                    char *uid = strstr(text, "Uid:");''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-063', 'baremetal-sdk-original-init-064')
compile(payload, 'original-graphics-064-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
