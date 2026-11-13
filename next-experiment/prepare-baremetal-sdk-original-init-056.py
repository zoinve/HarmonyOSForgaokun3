"""Observe trace-path visibility without changing original service credentials."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-055.py')))
source = parent['source'].replace('ORIGINAL_INIT055_', 'ORIGINAL_INIT056_').replace('GRAPHICS055_', 'GRAPHICS056_')
source = source.replace('/run/graphics-trace', '/data/graphics-trace')
old = '    DIR *dir = opendir("/data/graphics-trace");\n    if (!dir) return;'
assert source.count(old) == 1
source = source.replace(old, '''    struct stat directory_stat;
    int stat_rc = stat("/data/graphics-trace", &directory_stat);
    int stat_errno = errno;
    dprintf(1, "GRAPHICS056_TRACE_DIR sample=%u stat=%d errno=%d mode=%o uid=%u\\n", sample,
            stat_rc, stat_errno, stat_rc ? 0 : (unsigned)directory_stat.st_mode,
            stat_rc ? 0 : (unsigned)directory_stat.st_uid);
    DIR *dir = opendir("/data/graphics-trace");
    if (!dir) return;''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-055', 'baremetal-sdk-original-init-056')
compile(payload, 'original-graphics-056-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
