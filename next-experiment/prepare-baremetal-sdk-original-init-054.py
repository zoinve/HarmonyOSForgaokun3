"""Original service identities, RAM-only system/vendor graphics providers."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-050.py')))
source = parent['source'].replace('ORIGINAL_INIT050_', 'ORIGINAL_INIT054_').replace('GRAPHICS050_', 'GRAPHICS054_')
source = source.replace('strstr(text, "libGLES") || strstr(text, "libmali")',
                        'strstr(text, "libGLES") || strstr(text, "libmali") ||\n'
                        '                            strstr(text, "harmony-mesa") || strstr(text, "libc++")')
anchor = 'int main(void)'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
static void graphics_egl_054(void)
{
    directory("/run/system-lower", 0755);
    directory("/run/system-upper", 0755);
    directory("/run/system-work", 0755);
    if (mount("/system", "/run/system-lower", NULL, MS_BIND, NULL) ||
        mount(NULL, "/run/system-lower", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY, NULL))
        fail("readonly system lower bind");
    if (mount("overlay", "/system", "overlay", MS_NODEV,
              "lowerdir=/run/system-lower,upperdir=/run/system-upper,workdir=/run/system-work"))
        fail("RAM-only system graphics overlay");
    directory("/system/lib64/harmony-mesa", 0755);
    directory("/system/lib64/harmony-mesa/gbm", 0755);
    const char *names[] = {
        "libEGL_impl.so", "harmony-mesa/libEGL.so.1",
        "harmony-mesa/libGLESv1_CM.so.1", "harmony-mesa/libGLESv2.so.2",
        "harmony-mesa/libc++_shared.so", "harmony-mesa/libdrm.so.2",
        "harmony-mesa/libgallium-25.0.1.so", "harmony-mesa/libgbm.so.1",
        "harmony-mesa/gbm/dri_gbm.so"
    };
    for (unsigned i = 0; i < sizeof(names) / sizeof(names[0]); ++i) {
        char from[256], to[256], data[32768];
        snprintf(from, sizeof(from), "/graphics-egl/%s", names[i]);
        snprintf(to, sizeof(to), "/system/lib64/%s", names[i]);
        if (unlink(to) && errno != ENOENT) fail("overlay replacement unlink");
        int in = open(from, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        int out = open(to, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0644);
        if (in < 0 || out < 0) fail("EGL overlay open");
        ssize_t n;
        while ((n = read(in, data, sizeof(data))) > 0) {
            ssize_t done = 0;
            while (done < n) {
                ssize_t w = write(out, data + done, (size_t)(n - done));
                if (w <= 0) fail("EGL overlay write");
                done += w;
            }
        }
        if (n < 0 || fchmod(out, 0644) || close(in) || close(out)) fail("EGL overlay copy");
    }
    const char *links[][2] = {
        {"libGLESv1_impl.so", "harmony-mesa/libGLESv1_CM.so.1"},
        {"libGLESv2_impl.so", "harmony-mesa/libGLESv2.so.2"},
        {"libGLESv3_impl.so", "harmony-mesa/libGLESv2.so.2"},
        {"lab-softpipe-167", "harmony-mesa"}
    };
    for (unsigned i = 0; i < sizeof(links) / sizeof(links[0]); ++i) {
        char to[256];
        snprintf(to, sizeof(to), "/system/lib64/%s", links[i][0]);
        if (unlink(to) && errno != ENOENT) fail("EGL overlay alias unlink");
        if (symlink(links[i][1], to)) fail("EGL overlay alias");
    }
    dprintf(1, "GRAPHICS054_EGL original_nativewindow=1 platform_libcxx_replaced=0 private_mesa_ndk_runtime=1 service_credentials_unmodified=1 physical_gpu=0\n");
}

''' + anchor)
anchor = '    guest_permissive_config_047();'
assert source.count(anchor) == 1
source = source.replace(anchor, '    graphics_egl_054();\n' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-050', 'baremetal-sdk-original-init-054')
compile(payload, 'original-graphics-054-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
