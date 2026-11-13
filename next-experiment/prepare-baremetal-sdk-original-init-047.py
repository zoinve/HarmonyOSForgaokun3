"""Original full service graph, permissive guest-only configuration, passive evidence.

Safe non-main generator. Original SDK images, service credentials and policies
remain untouched; only a RAM file bind covers the guest SELinux mode config.
"""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-038.py')))
source = parent['source'].replace('ORIGINAL_INIT038_', 'ORIGINAL_INIT047_')
source = source.replace('enforcing=1', 'enforcing=0')
source = source.replace("buffer[0] != '1'", "buffer[0] != '0'")
source = source.replace('explicit opt-in/enforcing required', 'explicit opt-in/permissive required')
source = source.replace('SELinux enforcing before original init', 'SELinux permissive before original init')
anchor = 'int main(void)'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
static void guest_permissive_config_047(void)
{
    char config[4096];
    if (read_path("/system/etc/selinux/config", config, sizeof(config)) <= 0)
        fail("original SELinux config read");
    const char *key = "SELINUX=enforcing";
    char *position = strstr(config, key);
    if (!position || strstr(position + strlen(key), key)) fail("original mode config guard");
    int fd = open("/run/selinux-config-047", O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    if (fd < 0) fail("exclusive volatile SELinux config");
    size_t prefix = (size_t)(position - config);
    const char replacement[] = "SELINUX=permissive";
    const char *tail = position + strlen(key);
    if (write(fd, config, prefix) != (ssize_t)prefix ||
        write(fd, replacement, sizeof(replacement) - 1) != (ssize_t)(sizeof(replacement) - 1) ||
        write(fd, tail, strlen(tail)) != (ssize_t)strlen(tail) || close(fd))
        fail("volatile mode config write");
    if (mount("/run/selinux-config-047", "/system/etc/selinux/config", NULL, MS_BIND, NULL) ||
        mount(NULL, "/system/etc/selinux/config", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY, NULL))
        fail("guest-only readonly config bind");
    dprintf(1, "GRAPHICS047_CONFIG guest_only=1 mode=permissive policy_unmodified=1 service_credentials_unmodified=1\n");
}

static void graphics_observer_047(void)
{
    for (unsigned sample = 0; sample < 12; ++sample) {
        char text[8192], path[128];
        ssize_t n = read_path("/sys/fs/selinux/enforce", text, sizeof(text));
        dprintf(1, "GRAPHICS047_SELINUX sample=%u enforce=%c\n", sample, n > 0 ? text[0] : '?');
        DIR *processes = opendir("/proc");
        if (processes) {
            struct dirent *entry;
            while ((entry = readdir(processes))) {
                char *end = NULL;
                long pid = strtol(entry->d_name, &end, 10);
                if (!*entry->d_name || *end || pid <= 1) continue;
                snprintf(path, sizeof(path), "/proc/%ld/cmdline", pid);
                n = read_path(path, text, sizeof(text));
                if (n <= 0) continue;
                for (ssize_t i = 0; i < n; ++i) if (!text[i]) text[i] = ' ';
                if (!strstr(text, "render_service") && !strstr(text, "composer_host") &&
                    !strstr(text, "allocator_host") && !strstr(text, "foundation") &&
                    !strstr(text, "samgr") && !strstr(text, "hilogd") &&
                    !strstr(text, "devmgr") && !strstr(text, "param_watcher")) continue;
                dprintf(1, "GRAPHICS047_PROCESS sample=%u pid=%ld cmd=%s\n", sample, pid, text);
                snprintf(path, sizeof(path), "/proc/%ld/status", pid);
                if (read_path(path, text, sizeof(text)) > 0) {
                    char *uid = strstr(text, "Uid:");
                    if (uid) { char *nl = strchr(uid, '\n'); if (nl) *nl = 0;
                        dprintf(1, "GRAPHICS047_IDENTITY pid=%ld %s\n", pid, uid); }
                }
                snprintf(path, sizeof(path), "/proc/%ld/attr/current", pid);
                if (read_path(path, text, sizeof(text)) > 0)
                    dprintf(1, "GRAPHICS047_DOMAIN pid=%ld value=%s\n", pid, text);
                snprintf(path, sizeof(path), "/proc/%ld/maps", pid);
                FILE *maps = fopen(path, "r");
                if (maps) {
                    while (fgets(text, sizeof(text), maps)) {
                        if (strstr(text, "display_composer") || strstr(text, "display_buffer") ||
                            strstr(text, "libEGL") || strstr(text, "librender_service") ||
                            strstr(text, "libGLES") || strstr(text, "libmali"))
                            dprintf(1, "GRAPHICS047_MAP pid=%ld %s", pid, text);
                    }
                    fclose(maps);
                }
            }
            closedir(processes);
        }
        if (sample == 9) {
            pid_t log_child = fork();
            if (log_child == 0) {
                alarm(5);
                char *const args[] = {"/system/bin/hilog", "-x", NULL};
                execv(args[0], args);
                dprintf(1, "GRAPHICS047_HILOG_EXEC_ERROR errno=%d\n", errno);
                _exit(127);
            }
            if (log_child > 0) { int status = 0;
                if (waitpid(log_child, &status, 0) == log_child)
                    dprintf(1, "GRAPHICS047_HILOG_EXIT status=%d\n", status); }
        }
        sleep(5);
    }
    dprintf(1, "GRAPHICS047_OBSERVATION_END readiness_not_inferred=1\n");
    _exit(0);
}

''' + anchor)
source = '#include <signal.h>\n#include <sys/wait.h>\n' + source
anchor = '    char *const environment[] = '
assert source.count(anchor) == 1
source = source.replace(anchor, '''    guest_permissive_config_047();
    pid_t observer = fork();
    if (observer < 0) fail("passive graphics observer fork");
    if (observer == 0) graphics_observer_047();
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-038', 'baremetal-sdk-original-init-047')
compile(payload, 'original-graphics-047-build', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=180)
    raise SystemExit(result.returncode)
