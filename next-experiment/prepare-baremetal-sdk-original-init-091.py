"""Require an exact fresh 8 GiB test volume; never synthesize account data."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-090.py')))
source = parent['source'].replace('ORIGINAL_INIT090_', 'ORIGINAL_INIT091_').replace('GRAPHICS090_', 'GRAPHICS091_')
old = '"sdk-testdata", 1048576,'
assert source.count(old) == 1
source = source.replace(old, '"sdk-testdata", 16777216,')
anchor = '#include <sys/stat.h>'
assert source.count(anchor) == 2  # Bootstrap and inherited disk-selection header.
source = source.replace(anchor, anchor + '\n#include <sys/statvfs.h>', 1)
anchor = 'static void graphics_account_query_090('
assert source.count(anchor) == 1
position = source.index(anchor)
helper = r'''static void graphics_data_capacity_091(unsigned sample) {
    struct statvfs data;
    int rc = statvfs("/data", &data);
    int saved = errno;
    dprintf(1, "GRAPHICS091_DATA_CAPACITY sample=%u stat=%d errno=%d fragment=%llu blocks=%llu available=%llu\n",
            sample, rc, rc ? saved : 0,
            rc ? 0ULL : (unsigned long long)data.f_frsize,
            rc ? 0ULL : (unsigned long long)data.f_blocks,
            rc ? 0ULL : (unsigned long long)data.f_bavail);
}

'''
source = source[:position] + helper + source[position:]
anchor = 'static void graphics_account_query_090('
position = source.index('{', source.index(anchor)) + 1
source = source[:position] + '\n    graphics_data_capacity_091(sample);' + source[position:]
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-090', 'baremetal-sdk-original-init-091')
compile(payload, 'original-data-capacity-091-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
