"""Verify real QCA evidence without turning initialization into a full Bluetooth claim."""
from pathlib import Path
import runpy,json,re,hashlib
base=Path(__file__).resolve().parent
common=runpy.run_path(str(base/'verify-native-original-graphics-runtime-004.py'))['verify']
extract=runpy.run_path(str(base/'extract-native-faults-018.py'))['extract']
def verify(number):
    root=base.parent/f'reports/native-original-graphics-boot-{number:03}'
    result=common(root,data_bytes=3221225472)
    runtime=json.loads((root/'runtime-result.json').read_text())
    text=(root/'native-logs'/runtime['logs'][-1]['name']).read_bytes().decode(errors='replace')
    assert result['init_root_stable_verified']
    assert result['target_selinux_permissive_samples']==12
    assert 'ro,' in runtime['lab_mount'] and 'norecovery' in runtime['lab_mount']
    if number==21:
        assert 'real_reset_success=1' in text and '040e0401030c00' in text
        assert 'NATIVE_QCA021 power_status=0 uart_status=0 reset_status=0' in text
        result.update(real_native_controller_reset_verified=True,original_bluetooth_transport_fixed=False)
    else:
        assert number==22
        assert 'NATIVE_QCA022 real_channel_open=1 peer_uid=3021 errno=0' in text
        assert 'NATIVE_BT022 op=real_power_on result=0 errno=0 uid=3021' in text
        assert 'NATIVE_BT022 op=real_firmware_initialized result=0 errno=0 uid=3021' in text
        assert 'NATIVE_BT022 op=unsupported_operation result=-1 errno=95 uid=3021' in text
        assert 'TL_Startup success: 0' in text and 'event_finish_startup' in text
        commands=re.findall(r'NATIVE_QCA022 command opcode=([0-9a-f]{4}) bytes=(\d+)',text)
        replies=re.findall(r'NATIVE_QCA022 completion opcode=([0-9a-f]{4}) status=(\d+) bytes=(\d+)',text)
        assert ('0c03','0','7') in replies and ('0c03','4') in commands
        assert len(replies)>20
        # Real unsupported-command status must remain visible, not rewritten as success.
        assert ('0c6d','17','7') in replies
        observations=re.findall(r'NATIVE_DIAG002_PROCESS sample=(\d+) pid=(\d+) cmd=bluetooth_service\s*\n',text)
        assert len(observations)>=9 and len(set(pid for sample,pid in observations))==1
        pid=observations[0][1]
        assert not re.search(r'bluetooth_service\(pid \d+\) exit with signal',text)
        assert 'command_timed_out' not in text and 'startup_timer_expired' not in text
        assert 'restarting the Bluetooth process' not in text
        for row in runtime['logs']:
            snapshot=(root/'native-logs'/row['name']).read_bytes().decode(errors='replace')
            assert not re.search(r'exit with signal : (6|11)\b',snapshot),row['name']
        assert not extract(text)
        captures=re.findall(r'NATIVE_FAULT018_CAPTURE sample=(\d+) files=(\d+) bytes=(\d+)',text)
        assert captures==[(str(n),'0','0') for n in (2,5,8,11)]
        assert 'usual.event.SCREEN_UNLOCKED' in text
        bridge=json.loads((root/'qca-bridge.json').read_text())
        for name,key in [('native-qca-broker-022.c','broker_source_sha256'),('native-qca-vendor-022.c','vendor_source_sha256')]:
            assert hashlib.sha256((base/name).read_bytes()).hexdigest()==bridge[key]
        assert bridge['allowed_client_uid']==3021 and bridge['command_translation'] is False
        result.update(original_bluetooth_transport_fixed_in_observation=True,
                      real_controller_command_count=len(commands),real_controller_completion_count=len(replies),
                      actual_nonzero_controller_replies=[r for r in replies if r[1]!='0'],
                      bluetooth_service_pid=pid,bluetooth_service_samples=observations,
                      recorded_bluetooth_timeout_abort_or_restart=False,complete_fault_file_count=0,
                      second_independent_crash_identified=False,unsupported_lpm_reported_not_faked=True,
                      pairing_audio_suspend_and_long_term_stability_verified=False,
                      both_requested_crashes_fixed=False)
    return result
if __name__=='__main__':
    results={str(n):verify(n) for n in (21,22)}
    target=base.parent/'reports/native-qca-runtime-021-022-verification.json'
    with target.open('x') as f:json.dump(results,f,indent=2)
    print(json.dumps({k:{name:value for name,value in d.items() if name not in ('observed_processes','dac_states','init_root_data_states')} for k,d in results.items()},indent=2))
