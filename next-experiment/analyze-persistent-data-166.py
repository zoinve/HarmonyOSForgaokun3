"""Correlate native mount, backing-file checks, cross-boot marker and shutdown flush."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
UUID=r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'

def summarize(text,filesystem_uuid,expected_previous=None,expected_archived=5):
    markers=[dict(native_boot_id=boot,previous_present=int(present),previous=previous,archived=int(archived))
        for boot,present,previous,archived in re.findall(
            '^PERSISTENT166_RUNTIME disk_backed=1 seed_reset=0 boot=('+UUID+') previous_present=([01]) previous=(none|'+UUID+r') archived=(\d+)$',text,re.M)]
    ready=text.count('PERSISTENT166_READY nvme_backed=1 capacity=8589934592 seed_copied=0 inode_verified=1 exclusive_lock=1\n')==1
    loop=bool(re.search(r'^NATIVE_LOOP index=3 readonly=0 bytes=8589934592 ram_data=0$',text,re.M))
    mounts=re.findall(r'^\d+ \d+ 7:3 / /data rw,[^\n]* - ext4 /dev/loop3 rw,[^\n]*$',text,re.M)
    flush=text.count('PERSISTENT166_FLUSHED inner_syncfs=1 inner_unmounted=1 backing_fsync=1 outer_syncfs=1\n')==1
    finish=text.count('PERSISTENT166_FINISH status=0 clean_shutdown_not_inferred=0\n')==1
    handoff='readonly_images=4 volatile_data=0 persistent_data=1\n' in text
    reset=any(value in text for value in ['OOBE123_SEED_VERIFIED','NATIVE_RAM_DATA016','NATIVE_ORIGINAL_DATA ram_backed=1'])
    refused='PERSISTENT166_REFUSED' in text or 'NATIVE_ORIGINAL001_FAIL' in text
    marker_ok=False
    if len(markers)==1:
        m=markers[0]
        marker_ok=(m['previous_present']==0 and m['previous']=='none' and m['archived']==0) if expected_previous is None else (
            m['previous_present']==1 and m['previous']==expected_previous and m['native_boot_id']!=expected_previous and m['archived']==expected_archived)
    verified=ready and loop and bool(mounts) and flush and finish and handoff and not reset and not refused and marker_ok
    return dict(native_disk_mount_and_flush_verified=verified,filesystem_uuid=filesystem_uuid,
        native_boot_id=markers[0]['native_boot_id'] if len(markers)==1 else None,
        previous_native_boot_id=markers[0]['previous'] if len(markers)==1 and markers[0]['previous_present'] else None,
        backing_file_identity_and_lock_verified=ready,loop_is_writable_nvme_data=loop,
        original_runtime_data_mount_observed=bool(mounts),original_init_handoff_observed=handoff,
        inner_and_outer_flush_verified=flush and finish,seed_reset_observed=reset,
        storage_refusal_observed=refused,marker_chain_matches=marker_ok,markers=markers,
        application_settings_persistence_independently_tested=False)

if __name__=='__main__':
    assert sys.argv[1:] in [['166'],['167'],['168'],['169']]
    number=sys.argv[1]
    report=ROOT/('reports/commercial61-native-166-compile-fix-1' if number=='166' else 'reports/commercial61-native-'+number)
    evidence=report/'runtime-evidence'
    manifest=json.loads((evidence/'retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        data=(evidence/'raw'/name).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    latest=max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log',n)),key=lambda n:int(n[6:-4]))
    text=(evidence/'raw'/latest).read_text(errors='replace')
    previous=None
    if number!='166':
        prior='commercial61-native-166-compile-fix-1' if number=='167' else 'commercial61-native-'+str(int(number)-1)
        old=json.loads((ROOT/'reports'/prior/'persistent-offline-verification.json').read_text())
        assert old['filesystem_clean'] and old['disk_marker_matches_native_runtime']
        previous=old['native_boot_id']
    provision=json.loads((ROOT/'reports/persistent-data-165/provision.json').read_text())
    result=summarize(text,provision['filesystem_uuid'],previous,{'166':0,'167':5,'168':0,'169':5}[number])
    if number in ['168','169']:
        memory=text.count('PERSISTENT168_MEMORY_ARCHIVE previous_log_present=1 preserved=1\n')==1
        result['memory_prerequisite_log_archived']=memory
        result['native_disk_mount_and_flush_verified']=result['native_disk_mount_and_flush_verified'] and memory
    result.update(run=manifest['run'],phase_file=latest,all_retrieved_hashes_verified=True)
    (report/'persistent-runtime-analysis.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    if not result['native_disk_mount_and_flush_verified']:raise SystemExit('Native persistent-data acceptance incomplete')
