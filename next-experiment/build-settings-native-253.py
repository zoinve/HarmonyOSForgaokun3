"""Keep235 runtime and use a real-time observation deadline before900s fallback."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


if __name__ == '__main__':
    parent = BUILD / 'commercial61-native-235'
    work = BUILD / 'commercial61-native-253'
    report = ROOT / 'reports/commercial61-native-253'
    assert not work.exists() and not report.exists()
    work.mkdir(); report.mkdir()
    metadata = json.loads((ROOT / 'reports/commercial61-native-235/result.json').read_text())
    for row in metadata['artifacts']:
        if row['name'] not in {'init', 'init.c', 'initrd.img'}:
            os.link(parent / row['name'], work / row['name'])
    for name in ['persistent-data-166.h', 'persistent-data-172.h', 'persistent-unmount-plan-201.h', 'native-live-debug-159.h']:
        os.link(parent / name, work / name)
    source = (parent / 'init.c').read_text()
    assert source.count('/commercial61-native-235/bootstrap-runtime087') == 5
    source = source.replace('/commercial61-native-235/bootstrap-runtime087', '/commercial61-native-253/bootstrap-runtime087')
    helper = '''static int settings253_budget(unsigned requested)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) return 0;
    return diag_budget_allow(budget_start, now.tv_sec + now.tv_nsec / 1e9,
                             900, 180, requested);
}
'''
    source = once(source, 'static double budget_start = -1;\n', 'static double budget_start = -1;\n\n' + helper)
    source = once(source, 'for(unsigned i=0;i<14;++i){', 'for(unsigned i=0;i<14 && settings253_budget(45);++i){')
    source = once(source, 'for(unsigned elapsed033=70;elapsed033<720;++elapsed033){',
                  'for(unsigned elapsed033=70;elapsed033<720 && settings253_budget(45);++elapsed033){')
    source = once(source, 'COMMERCIAL087_RUNNING target_budget_seconds=720',
                  'COMMERCIAL253_RUNNING monotonic_work_deadline_seconds=720 cleanup_reserve_seconds=180')
    (work / 'init.c').open('x').write(source)
    proc = subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
        '-I', str(ROOT / 'next-experiment'), str(work / 'init.c'),
        str(ROOT / 'next-experiment/baremetal-diagnostic-core.c'), '-o', str(work / 'init')], capture_output=True)
    if proc.stderr:
        (report / 'compile.stderr').open('xb').write(proc.stderr)
    assert proc.returncode == 0, proc.stderr.decode()
    sha = lambda value: hashlib.sha256(value).hexdigest()
    members = runpy.run_path(str(ROOT / 'next-experiment/audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(ROOT / 'next-experiment/build-commercial-native-087.py'))['member']
    full = {name: (mode, data) for name, mode, data in members(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    old_init = full['init'][1]
    full['init'] = (full['init'][0], (work / 'init').read_bytes())
    mode, wrapper = full['early-hardware093.sh']
    assert wrapper.count(sha(old_init).encode()) == 1
    full['early-hardware093.sh'] = (mode, wrapper.replace(sha(old_init).encode(), sha(full['init'][1]).encode(), 1))
    def archive(entries):
        raw = b''.join(member(name, mode, data, index + 1) for index, (name, (mode, data)) in enumerate(entries.items()))
        return gzip.compress(raw + member('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(full))
    overlay = {name: (mode, data) for name, mode, data in members(gzip.decompress((parent / 'minimal-overlay.img').read_bytes()))}
    for name in ['init', 'early-hardware093.sh']:
        overlay[name] = full[name]
    data = archive(overlay)
    (work / 'minimal-overlay.img').open('xb').write(data)
    for row in metadata['artifacts']:
        value = (work / row['name']).read_bytes()
        row.update(bytes=len(value), sha256=sha(value))
    metadata.pop('settings235')
    metadata.update(outer_deadline_seconds=900, target_budget_seconds=720, runtime_verified=False,
        settings253=dict(monotonic_observation_budget=True, cleanup_reserve_seconds=180,
            per_iteration_work_admission_seconds=45, original_aa_launch_requests=0,
            desktop173_runtime_unchanged=True, prior249_tree_equality_gate_failed=True,
            further_storage_validation_skipped_at_user_request=True,
            historical_admission_suite_not_rerun=True, settings_window_verified=False))
    overlay_result = json.loads((ROOT / 'reports/commercial61-native-235/overlay-result.json').read_text())
    overlay_result.update(bytes=len(data), sha256=sha(data), chain=overlay_result['chain'][:-1] + ['commercial61-native-253/initrd.img'])
    overlay_result.pop('ordered_chain_equals_full_235', None)
    overlay_result['independent_chain_admission_not_rerun_at_user_request'] = True
    (report / 'result.json').open('x').write(json.dumps(metadata, indent=2))
    (report / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    print(json.dumps(dict(build='253', compiled=True, overlay_bytes=len(data), admission_suite_rerun=False)))
