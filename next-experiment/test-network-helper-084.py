"""Reuse exact-command tests against the generated association helper."""
from pathlib import Path
import importlib.util
import runpy
import unittest

b = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('commands083', b / 'test-network-supplicant-083.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.SOURCE = runpy.run_path(str(b / 'commercial-network-helper-084.py'))['SOURCE']
module.STUB = module.STUB.replace('-c/network083/wpa.conf', '-c/network084/wpa.conf')


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(module.CommandTests))
    raise SystemExit(not result.wasSuccessful())
