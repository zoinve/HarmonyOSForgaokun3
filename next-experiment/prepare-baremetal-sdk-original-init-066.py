"""Observe genuine dictionary files and request the original service's screen dump."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-064.py')))
source = parent['source'].replace('ORIGINAL_INIT064_', 'ORIGINAL_INIT066_').replace('GRAPHICS064_', 'GRAPHICS066_')
anchor = '        long rs_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + r'''
        if (sample == 9 || sample == 13 || sample == 17) {
            const char *dict_path = "/data/log/dict/2C/EB723E313C80C3605ECD369C0B8CB6";
            struct stat st;
            int rc = stat(dict_path, &st);
            int saved = errno;
            char resolved[4096];
            char *real = realpath(dict_path, resolved);
            dprintf(1, "GRAPHICS066_DICT_FILE sample=%u stat=%d errno=%d size=%lld mode=%o real=%s\n",
                    sample, rc, rc ? saved : 0, rc ? -1LL : (long long)st.st_size,
                    rc ? 0U : (unsigned)st.st_mode, real ? real : "<none>");
            int fd = open(dict_path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
            unsigned char head[16];
            ssize_t got = fd < 0 ? -1 : read(fd, head, sizeof(head));
            dprintf(1, "GRAPHICS066_DICT_READ sample=%u bytes=%ld errno=%d head=", sample,
                    (long)got, got < 0 ? errno : 0);
            for (ssize_t k = 0; k < got; ++k) dprintf(1, "%02x", head[k]);
            dprintf(1, "\n");
            if (fd >= 0) close(fd);
        }
        if (sample == 15) {
            dprintf(1, "GRAPHICS066_SCREEN_DUMP original_tool=1 original_service=1\n");
            pid_t dump_child = fork();
            if (dump_child == 0) {
                alarm(12);
                char *const args[] = {"/system/bin/hidumper", "-s", "RenderService", "-a", "screen", NULL};
                execv(args[0], args);
                dprintf(1, "GRAPHICS066_SCREEN_DUMP_EXEC_ERROR errno=%d\n", errno);
                _exit(72);
            }
            if (dump_child > 0) {
                int dump_status = -1;
                while (waitpid(dump_child, &dump_status, 0) < 0 && errno == EINTR) {}
                dprintf(1, "GRAPHICS066_SCREEN_DUMP_END status=%d\n", dump_status);
            }
        }''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-064', 'baremetal-sdk-original-init-066')
compile(payload, 'original-graphics-066-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
