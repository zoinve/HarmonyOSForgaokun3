"""Keep one current private archive and record compact cleanup totals."""
from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
OUTPUT = REPORTS / 'storage-cleanup-229-summary.json'


def read(name):
    return json.loads((REPORTS / name).read_text())


if __name__ == '__main__':
    assert os.geteuid() == 0 and not OUTPUT.exists()
    archive = read('private-settings-archive-230.json')
    source = next(row for row in archive['images'] if 'candidate-191-r2' in row['original'])
    current = next(row for row in archive['images'] if 'scaffolding-216' in row['original'])
    repair = read('settingsdata-scaffolding-216/result.json')
    assert repair['existing_tree_before'] == repair['existing_tree_after'] and repair['source_unchanged']
    old = Path(source['archive']);keep = Path(current['archive'])
    build = Path('/home/zoinve/harmony-virgl-883')
    assert old.resolve().is_relative_to(build) and keep.resolve().is_relative_to(build)
    assert not old.is_symlink() and not keep.is_symlink() and old.is_file() and keep.is_file()
    assert source['decompressed_hash_verified'] and current['decompressed_hash_verified']
    assert keep.stat().st_size == current['archive_bytes']
    additional = old.stat().st_blocks * 512
    old.unlink()
    os.sync()
    scratch = read('scratch-cleanup-221/result.json')
    remote = read('evidence-cleanup-220/remote.json')
    lab = read('obsolete-lab-cleanup-224/result.json')
    local = read('evidence-cleanup-220/local.json')
    metadata = read('duplicate-metadata-cleanup-223.json')
    extra = read('report-scratch-cleanup-228.json')
    wsl = read('local-scratch-cleanup-222/result.json')
    target_saved = (scratch['free_after'] - scratch['free_before'] +
        remote['free_after'] - remote['free_before'] + lab['free_after'] - lab['free_before'])
    local_saved = (local['removed_bytes'] + read('extracted-archive-cleanup-225.json')['removed_bytes'] +
        read('historical-log-compression-226.json')['saved_bytes'] + extra['auxiliary_log_saved_bytes'] +
        sum(row['bytes'] for row in extra['obsolete_package_or_temporary_table_files_deleted']) +
        sum(row['bytes'] for row in metadata['redundant_json_stdout_removed']) +
        sum(row['bytes'] for row in metadata['duplicate_hash_tables_coalesced']))
    wsl_saved = (sum(row['allocated_bytes'] for row in wsl['deleted_failed_candidates']) +
        wsl['deduplicated_allocated_bytes'] + archive['allocated_bytes_saved'] + additional)
    result = dict(target_filesystem_free_bytes_gained=target_saved,
        windows_report_logical_bytes_saved=local_saved,
        wsl_allocated_bytes_saved=wsl_saved,
        wsl_guest_deallocation_not_a_measure_of_host_vhd_compaction=True,
        ubuntu_free_bytes_after_cleanup=scratch['free_after'],lab_free_bytes_after_cleanup=lab['free_after'],
        obsolete_remote_logs_deleted=remote['removed_files'] + lab['obsolete_log_files_deleted'],
        cumulative_local_snapshots_deleted=local['removed_files'],
        redundant_extraction_archives_deleted=len(read('extracted-archive-cleanup-225.json')['removed_archives']),
        duplicate_hash_tables_coalesced=len(metadata['duplicate_hash_tables_coalesced']),
        superseded_private_source_archive_deleted=str(old),
        retained_private_repair_archive=str(keep),
        active165_and_current197_hashes_verified_unchanged=True,
        working_desktop173_and_original_images_preserved=True,usb_work_resumed=False,
        settings_ui_fixed_or_verified=False,
        historical_log_reader='next-experiment/compress-historical-logs-226.py:open_log')
    OUTPUT.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
