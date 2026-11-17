"""Keep USB kernel, original-root visibility and actual file access distinct."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/commercial61-native-175-compile-fix-1'


def summarize(text):
    protections = re.findall(r'^USB175_PROTECTED name=(\w+) vid=346d pid=5678 major=(\d+) minor=(\d+) bytes=(\d+) before=([01]) after=1 kernel_flag_only=1 media_data_writes=0$', text, re.M)
    starts = re.findall(r'^NATIVE_ORIGINAL_START real_pid=(\d+) original_pid_in_namespace=1 credentials_unmodified=1$', text, re.M)
    sample_pattern = r'^USBSTORAGE174_BEGIN target=(\d+) mono_ms=(\d+) read_only=1 service_acceptance_not_inferred=1$'
    samples = []
    for match in re.finditer(sample_pattern, text, re.M):
        end = text.find('USBSTORAGE174_END ', match.end())
        if end < 0: continue
        chunk = text[match.end():end]
        blocks = []
        for row in re.findall(r'^USBSTORAGE174_BLOCK (.+)$', chunk, re.M):
            values = dict(field.split('=',1) for field in row.split())
            assert set(values)=={'name','vid','pid','major','minor','sectors','ro','removable','partition','target_dev_available','matching_target_nodes','node_scan_complete'}
            assert re.fullmatch(r'[A-Za-z0-9_.-]+',values['name'])
            assert re.fullmatch(r'[0-9a-f]{4}',values['vid']) and re.fullmatch(r'[0-9a-f]{4}',values['pid'])
            values.update({key:int(value) for key,value in values.items() if key not in ['name','vid','pid']})
            blocks.append(values)
        helpers = dict((name,int(present)) for name,present in re.findall(r'^USBSTORAGE174_HELPER name=([a-z.]+) executable_file_present=([01]) executed=0$',chunk,re.M))
        fuse = re.findall(r'^USBSTORAGE174_FUSE target_node_present=([01])$',chunk,re.M)
        samples.append(dict(target=int(match[1]),monotonic_ms=int(match[2]),blocks=blocks,
                            original_helpers=helpers,fuse_node_present=int(fuse[0]) if len(fuse)==1 else None))
    disks = [block for sample in samples for block in sample['blocks'] if block['vid']=='346d' and block['pid']=='5678' and block['partition']==-1]
    identity = len(protections)==1 and len(starts)==1 and bool(samples) and all(str(row['target'])==starts[0] for row in samples)
    protected = identity and int(protections[0][3])==61849600*512 and bool(disks) and all(
        block['sectors']==61849600 and block['ro']==1 and block['removable']==1 and
        block['major']==int(protections[0][1]) and block['minor']==int(protections[0][2]) for block in disks)
    return dict(protection_records=[dict(name=row[0],major=int(row[1]),minor=int(row[2]),bytes=int(row[3]),previous_readonly=int(row[4])) for row in protections],
        samples=samples,native_target_identity_matches=identity,kernel_usb_disk_readonly_verified=protected,
        late_usb_sampling_observed=any(row['monotonic_ms']>=100000 for row in samples),
        any_matching_original_root_block_node_observed=any(block['matching_target_nodes']>0 for sample in samples for block in sample['blocks']),
        node_search_bounds=dict(maximum_depth=4,maximum_entries_per_identity=1024,exhaustive_absence_not_inferred=True),
        original_usb_service_device_list_verified=False,original_file_manager_access_verified=False,
        media_file_contents_read_by_new_probe=False,usb_serials_exported_by_new_probe=False,
        settings_repair_claimed=False)


if __name__ == '__main__':
    output = REPORT / 'usb-storage-analysis.json'
    assert not output.exists()
    evidence = REPORT / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name,expected in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256'],name
    latest = max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)),key=lambda name:int(name[6:-4]))
    result = summarize((evidence / 'raw' / latest).read_text(errors='replace'))
    result.update(run=manifest['run'],phase_file=latest,verified_evidence_files=len(manifest['files']))
    output.open('x').write(json.dumps(result,indent=2))
    print(json.dumps({key:value for key,value in result.items() if key!='samples'},indent=2))
    assert result['kernel_usb_disk_readonly_verified'], 'native protection/USB identity is not yet proven'
