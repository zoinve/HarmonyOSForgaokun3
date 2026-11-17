"""Export bounded read-only disassembly and correct a boolean log interpretation."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'reports/devicedetect-server-static-102'


if __name__ == '__main__':
    output = FOLDER/'analysis.json'
    assert not output.exists()
    service = FOLDER/'libcollabfwk_devicedetect_service.local-policy-v1.so'
    base = FOLDER/'libcollaborationfwk_service_base.z.so'
    ranges = [('service-query-entry', service, 0x15683c, 0x1568dc),
              ('local-info-update', base, 0x4119c, 0x412c8),
              ('local-info-readers', base, 0x41d84, 0x41f60)]
    exports = []
    for name, binary, start, stop in ranges:
        text = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d', '-C',
            f'--start-address={start}', f'--stop-address={stop}', str(binary)], text=True)
        path = FOLDER/(name+'.txt')
        path.open('x').write(text)
        exports.append(dict(path=path.name, start=start, stop=stop,
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    reader = (FOLDER/'local-info-readers.txt').read_text()
    assert '41ec0:\tf100011f' in reader and 'cmp\tx8, #0x0' in reader
    assert '41ec8:\t1a9f17e8' in reader and 'cset\tw8, eq' in reader
    assert '41ed4:\tb90013e8' in reader
    result = dict(binaries=[dict(path=p.name, bytes=p.stat().st_size,
                    sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (service, base)],
                  exports=exports,
                  boolean_log_interpretation=dict(text='localDeviceInfo is nullptr 0',
                    comparison='pointer == nullptr', logged_value=0,
                    pointer_is_null=False, network_id_nonempty_not_proven=True),
                  correction='Null-related field names in devicedetect-server-audit-102.json identify literal log text, not a null pointer. This analysis supersedes that interpretation; prior output remains unchanged.',
                  static_findings=[
                    'Service query entry calls GetLocalDeviceUdid, GetLocalDeviceNetworkId, GetLocalDeviceType before stage 1 logging.',
                    'GetLocalDeviceUdid takes shared lock and can update under exclusive lock when cached info is absent.',
                    'GetLocalDeviceNetworkId calls UpdateLocalDeviceInfoInLock before the boolean log.',
                    'UpdateLocalDeviceInfoInLock calls the original DeviceManager singleton and a virtual method. Exact runtime blocking instruction is not proven.'
                  ], target_booted=False, original_images_modified=False,
                  runtime_service_stack_still_needed=True, desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
