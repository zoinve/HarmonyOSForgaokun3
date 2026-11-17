"""Privacy/selection fixture only, never device or pairing acceptance."""
from io import BytesIO
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    inspect = runpy.run_path(str(BASE / 'analyze-bluetooth-link-468.py'))['inspect']
    data = b'''bluetooth_service (Connect:123) address=AA:BB:CC:DD:EE:FF name=fixture_private_name result=-5
bluetooth_service (OnPair:124) passkey=123456 status=987654
bluetooth_service (OnPair:125) code=765432 status=0
other_service (Connect:126) result=999
bluetooth_service (StartScan:127) result=1
'''
    result = inspect(BytesIO(data))
    assert result['function_counts'] == {'Connect': 1, 'OnPair': 2}
    records = result['last_link_profile_records']
    assert records[0]['numeric_fields'] == [{'field': 'result', 'value': '-5'}]
    assert records[1]['numeric_fields'] == []
    assert records[2]['numeric_fields'] == [{'field': 'status', 'value': '0'}]
    encoded = json.dumps(result)
    assert all(secret not in encoded for secret in ['123456', '987654', '765432', 'AA:BB', 'fixture_private_name'])
    print('BT469 original_service_selection_numeric_status_privacy=pass physical_pairing=0')
