"""Build a bounded repaired-provider observation; keep desktop173 runtime intact."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


if __name__ == '__main__':
    parent = BUILD / 'commercial61-native-206'
    work = BUILD / 'commercial61-native-235'
    report = ROOT / 'reports/commercial61-native-235'
    assert not work.exists() and not report.exists()
    repair = json.loads((ROOT / 'reports/settingsdata-orphan-repair-234/result.json').read_text())
    assert repair['final_read_only_fsck_exit'] == 0 and repair['active165_sha256_verified_unchanged']
    assert repair['existing_tree_before'] == repair['existing_tree_after'] and repair['private_pre231_backup_retained']
    metadata = json.loads((ROOT / 'reports/commercial61-native-206/result.json').read_text())
    previous = json.loads((ROOT / 'reports/commercial61-native-206/overlay-result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((parent / row['name']).read_bytes()) == row['sha256']
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    member = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {name: (mode, data) for name, mode, data in parser(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    work.mkdir()
    report.mkdir()
    for row in metadata['artifacts']:
        if row['name'] not in {'init', 'init.c', 'initrd.img'}:
            os.link(parent / row['name'], work / row['name'])
    headers = ['persistent-data-166.h', 'persistent-data-172.h', 'persistent-unmount-plan-201.h', 'native-live-debug-159.h']
    for name in headers:
        (work / name).open('xb').write((parent / name).read_bytes())
    adapt = runpy.run_path(str(BASE / 'settings-native-235.py'))
    (work / 'init.c').open('x').write(adapt['outer235']((parent / 'init.c').read_text()))
    args = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
            '-I', str(BASE), str(work / 'init.c'), str(BASE / 'baremetal-diagnostic-core.c'), '-o', str(work / 'init')]
    proc = subprocess.run(args, capture_output=True, timeout=120)
    if proc.stderr:
        (report / 'init.stderr').open('xb').write(proc.stderr)
    assert proc.returncode == 0, proc.stderr.decode()
    after = dict(before)
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    mode, wrapper = before['early-hardware093.sh']
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (mode, wrapper.replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    delta = {name: row for name, row in after.items() if before.get(name) != row}
    assert set(delta) == {'init', 'early-hardware093.sh'}
    def archive(entries):
        data = b''.join(member(name, mode, payload, index + 1)
                        for index, (name, (mode, payload)) in enumerate(entries.items()))
        return gzip.compress(data + member('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    minimal = {name: (mode, data) for name, mode, data in parser(gzip.decompress((parent / 'minimal-overlay.img').read_bytes()))}
    minimal.update(delta)
    overlay = archive(minimal)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    replay = dict(before)
    replay.update({name: (mode, data) for name, mode, data in parser(gzip.decompress(overlay))})
    assert replay == after
    for name in ['bootstrap-runtime087', 'bootstrap-runtime087.c']:
        assert (work / name).read_bytes() == (BUILD / 'commercial61-native-173' / name).read_bytes()
    assert sha((work / 'bootstrap-runtime087').read_bytes()) == 'fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122'
    metadata['artifacts'] = [dict(name=row['name'], bytes=(work / row['name']).stat().st_size,
                                sha256=sha((work / row['name']).read_bytes())) for row in metadata['artifacts']]
    metadata.pop('settings206')
    metadata['runtime_verified'] = False
    metadata['settings235'] = dict(expected_preboot_candidate_sha256=repair['candidate_after_sha256'],
        desktop173_runtime_and_source_byte_identical=True, original_aa_launch_requests=0,
        original_sandbox_and_watchdog_preserved=True, early_namespace_pin=True,
        early_sampling_non_reaping_waitid=True, successful_cumulative_snapshots_retained=2,
        target_observation_loop_seconds=720, fallback_reboot_seconds=900,
        active_data165_modified=False, usb_work_paused=True, installed_or_booted=False,
        settings_window_verified=False, header_hashes={name: sha((work / name).read_bytes()) for name in headers})
    overlay_result = dict(previous, bytes=len(overlay), sha256=sha(overlay),
        chain=previous['chain'][:-1] + ['commercial61-native-235/initrd.img'],
        ordered_chain_equals_full_235=True, parent_full_sha256=sha((parent / 'initrd.img').read_bytes()),
        chain_verification_basis='full206_plus235_overlay_pending_independent_admission')
    overlay_result.pop('ordered_chain_equals_full_206')
    (report / 'result.json').open('x').write(json.dumps(metadata, indent=2))
    (report / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    print(json.dumps(metadata['settings235'], indent=2))
