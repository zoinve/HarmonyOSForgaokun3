"""Exercise inherited exact commands against the new namespace helper."""
from pathlib import Path
import importlib.util
import runpy
import unittest

b = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('commands085', b / 'test-network-helper-085.py')
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
parent.module.SOURCE = runpy.run_path(str(b / 'commercial-network-helper-086.py'))['SOURCE']

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(parent.ProbeTests))
    raise SystemExit(not result.wasSuccessful())
