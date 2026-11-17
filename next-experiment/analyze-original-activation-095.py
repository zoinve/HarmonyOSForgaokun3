"""Trace the target's preserved native activation failures without replaying them."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE / 'analyze-original-devicedetect-095.py').read_text()
source = source.replace('original-devicedetect-095.json', 'original-activation-095.json')
source = source.replace('collabfwk|devicedetect|device.?detect|cfwk|devicepicker|CollaborationFwk',
    'TEEC|socIdCert|DeviceCert|dcm_service|hdi.*dcm|dcm.*hdi|tee_client|tzdriver|tc_ns|/dev/tee|ActivateDevice|activation.*(?:fail|error)|activate.*(?:fail|error)')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
