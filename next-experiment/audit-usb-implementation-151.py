"""Complete 150's unresolved fast symlinks without overwriting its evidence."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    read = runpy.run_path(str(BASE / 'audit-board-driver-contracts-126.py'))['read']
    runpy.run_path(str(BASE / 'audit-usb-implementation-150.py'))['collect'](read, 'usb-implementation-151')
