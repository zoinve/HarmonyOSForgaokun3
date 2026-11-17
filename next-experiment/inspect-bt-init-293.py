from pathlib import Path
import json
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    read = runpy.run_path(str(BASE / 'inspect-radio-contracts-259.py'))['read']
    data = read('p109-vendor.kr990-ext4-v1.img', '/lib64/libhci_interface_service_1.0.z.so')
    with tempfile.TemporaryDirectory(prefix='radio-abi293-') as tmp:
        path = Path(tmp) / 'hci.so'
        path.write_bytes(data)
        output = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d',
            '--start-address=0xef58', '--stop-address=0xf4c8', str(path)], text=True)
    report = BASE.parent / 'reports/bt-init-contract-293.txt'
    report.open('x').write(output)
    print(output)
