"""Preserve pinned primary kernel sources without a Windows full checkout."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / 'references/openharmony-kernel-113'
OUT = ROOT / 'reports/kernel-memcg-source-113'
REV = '2d4c72dffe4a20fe9e3892713ce10b659a78981a'
SOURCES = ['mm/memcg_control.c', 'mm/zswapd_control.c', 'mm/zswapd.c',
           'mm/zswapd_internal.h', 'mm/Kconfig', 'include/linux/zswapd.h',
           'include/linux/memcontrol.h', 'mm/Makefile']


def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args],
                          capture_output=True, check=True).stdout


if __name__ == '__main__':
    assert git('rev-parse', 'HEAD').decode().strip() == REV
    assert not OUT.exists(), 'Evidence already exists'
    OUT.mkdir()
    files = []
    tokens = ['zswapd_single_memcg_param', 'app_score', 'ub_mem2zram_ratio',
              'ub_zram2ufs_ratio', 'refault_threshold', 'HYPERHOLD_MEMCG',
              'cgroup_add_legacy_cftypes', 'get_next_memcg']
    for source in SOURCES:
        data = git('show', REV + ':' + source)
        (OUT / source.replace('/', '__')).open('xb').write(data)
        hits = [dict(line=i, text=line) for i, line in enumerate(data.decode().splitlines(), 1)
                if any(token in line for token in tokens)]
        files.append(dict(source=source, sha256=hashlib.sha256(data).hexdigest(),
                          bytes=len(data), relevant_lines=hits))
        print(source, len(data), 'bytes', len(hits), 'relevant lines')
    result = dict(revision=REV, files=files, original_kernel_modified=False,
                  target_boot_performed=False, source_only_not_ported_or_verified=True)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
