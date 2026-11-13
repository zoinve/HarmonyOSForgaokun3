"""Volatile vendor VDI overlay under the unchanged original service graph."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-048.py')))
source = parent['source'].replace('ORIGINAL_INIT048_', 'ORIGINAL_INIT050_').replace('GRAPHICS048_', 'GRAPHICS050_')
anchor = 'int main(void)'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
static void graphics_provider_050(void)
{
    DIR *devices = opendir("/sys/bus/virtio/devices");
    if (devices) {
        struct dirent *e;
        while ((e = readdir(devices))) {
            if (e->d_name[0] == '.') continue;
            char path[512], value[128], driver[512];
            snprintf(path, sizeof(path), "/sys/bus/virtio/devices/%.200s/device", e->d_name);
            if (read_path(path, value, sizeof(value)) <= 0) continue;
            snprintf(path, sizeof(path), "/sys/bus/virtio/devices/%.200s/driver", e->d_name);
            ssize_t n = readlink(path, driver, sizeof(driver) - 1);
            if (n < 0) strcpy(driver, "UNBOUND"); else driver[n] = 0;
            dprintf(1, "GRAPHICS050_VIRTIO name=%s id=%s driver=%s\n", e->d_name, value, driver);
        }
        closedir(devices);
    }
    DIR *drm = opendir("/sys/class/drm");
    unsigned nodes = 0;
    if (drm) {
        directory("/dev/dri", 0755);
        struct dirent *e;
        while ((e = readdir(drm))) {
            if (strncmp(e->d_name, "card", 4) && strncmp(e->d_name, "renderD", 7)) continue;
            char path[512], value[128];
            snprintf(path, sizeof(path), "/sys/class/drm/%.200s/dev", e->d_name);
            if (read_path(path, value, sizeof(value)) <= 0) continue;
            unsigned maj, min;
            if (sscanf(value, "%u:%u", &maj, &min) != 2) fail("genuine DRM dev_t");
            snprintf(path, sizeof(path), "/dev/dri/%.200s", e->d_name);
            if (mknod(path, S_IFCHR | 0660, makedev(maj, min)) && errno != EEXIST)
                fail("kernel-backed virtual DRM node");
            if (chown(path, 0, 1003) || chmod(path, 0660)) fail("graphics group device permissions");
            dprintf(1, "GRAPHICS050_DEVICE path=%s dev=%u:%u uid=0 gid=1003 mode=0660\n", path, maj, min);
            ++nodes;
        }
        closedir(drm);
    }
    if (!nodes) fail("virtual DRM kernel nodes absent; no fake devices");
    directory("/run/vendor-lower", 0755);
    directory("/run/vendor-upper", 0755);
    directory("/run/vendor-work", 0755);
    if (mount("/vendor", "/run/vendor-lower", NULL, MS_BIND, NULL) ||
        mount(NULL, "/run/vendor-lower", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY, NULL))
        fail("readonly vendor lower bind");
    if (mount("overlay", "/vendor", "overlay", MS_NODEV,
              "lowerdir=/run/vendor-lower,upperdir=/run/vendor-upper,workdir=/run/vendor-work"))
        fail("RAM-only vendor overlay");
    directory("/vendor/lib64/harmony-graphics", 0755);
    const char *names[] = {"libdisplay_composer_vdi_impl.z.so", "libdisplay_buffer_vdi_impl.z.so", "libdrm.so.2"};
    for (unsigned i = 0; i < 3; ++i) {
        char from[256], to[256], data[32768];
        snprintf(from, sizeof(from), "/graphics-provider/%s", names[i]);
        snprintf(to, sizeof(to), "/vendor/lib64/%s%s", i == 2 ? "harmony-graphics/" : "", names[i]);
        int in = open(from, O_RDONLY | O_CLOEXEC);
        int out = open(to, O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
        if (in < 0 || out < 0) fail("provider overlay file open");
        ssize_t n;
        while ((n = read(in, data, sizeof(data))) > 0) {
            ssize_t done = 0;
            while (done < n) {
                ssize_t w = write(out, data + done, (size_t)(n - done));
                if (w <= 0) fail("provider overlay write");
                done += w;
            }
        }
        if (n < 0 || fchmod(out, 0644) || close(in) || close(out)) fail("provider overlay copy");
    }
    dprintf(1, "GRAPHICS050_PROVIDER original_init_services=1 service_credentials_unmodified=1 volatile_vendor_only=1 physical_gpu=0\n");
}

''' + anchor)
anchor = '    guest_permissive_config_047();'
assert source.count(anchor) == 1
source = source.replace(anchor, '    graphics_provider_050();\n' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-048', 'baremetal-sdk-original-init-050')
compile(payload, 'original-graphics-050-build', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=180)
    raise SystemExit(result.returncode)
