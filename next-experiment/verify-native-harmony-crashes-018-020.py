"""Read-only crash evidence verification; never mistake SIGKILL for a full repair."""
from pathlib import Path
import runpy,json,hashlib,re
base=Path(__file__).resolve().parent
common=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
extract=runpy.run_path(str(base/'extract-native-faults-018.py'))['extract']
def verify(number):
    root=base.parent/f'reports/native-original-graphics-boot-{number:03}'
    d=common(root,data_bytes=3221225472)
    r=json.loads((root/'runtime-result.json').read_text())
    text=(root/'native-logs'/r['logs'][-1]['name']).read_bytes().decode(errors='replace')
    faults=extract(text)
    assert all(f'NATIVE_FAULT018_CAPTURE sample={n} ' in text for n in (2,5,8,11))
    assert 'usual.event.SCREEN_UNLOCKED' in text
    d.update(trial=number,snapshots_verified=len(r['logs']),
             complete_fault_file_count=len(faults),
             second_independent_crash_identified=False,
             bluetooth_functional=False,crash_repair_complete=False)
    if number==18:
        assert len(faults)==3
        manifest=json.loads((root/'fault-extraction.json').read_text())
        for row in manifest:
            data=(root/'fault-files'/row['name']).read_bytes()
            assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
            assert any(f['data']==data for f in faults)
        crash=json.loads(next(f['data'] for f in faults if f['path'].endswith('.json')))
        details=b'\n'.join(f['data'] for f in faults).decode(errors='replace')
        assert 'bluetooth_service' in details and 'SIGABRT' in details
        assert 'command_timed_out' in details and 'restarting the Bluetooth process' in details
        assert re.search(r'bluetooth_service\(pid 467\) exit with signal : 6',text)
        d.update(confirmed_process='bluetooth_service',confirmed_signal='SIGABRT',
                 confirmed_root_boundary='HCI Reset 0x0c03 timeout followed by original abort timer',
                 original_report_metadata_preserved=True)
    else:
        assert not faults
        assert not re.search(r'exit with signal : (6|11)\b',text)
        assert 'restarting the Bluetooth process' not in text
        assert re.search(r'bluetooth_service\(pid \d+\) exit with signal : 9',text)
        d.update(recorded_sigabrt_or_sigsegv=False,
                 bluetooth_service_sigkill_restart_remains=True,
                 failure_path_guard_is_not_a_complete_fix=True)
        if number==20:
            assert 'NATIVE_BT020 unavailable reason=missing_virtio_transport errno=2 uid=3021 success_callback=0' in text
            assert 'vendorInterface_->init failed.' in text
            assert 'hdiInit failed: 2' in text
            assert 'startup_timer_expired' in text and 'kill bt hidl abort' in text
            d.update(real_original_blue_host_observed_failure=True,
                     real_transport_failure_uid=3021,
                     upper_stack_startup_timeout_kill_observed=True)
    return d
if __name__=='__main__':
    results=[verify(n) for n in (18,19,20)]
    target=base.parent/'reports/native-harmony-crashes-018-020-verification.json'
    with target.open('x') as f:json.dump(results,f,indent=2)
    print(json.dumps([{k:v for k,v in d.items() if k not in ('observed_processes','dac_states','init_root_data_states')} for d in results],indent=2))
