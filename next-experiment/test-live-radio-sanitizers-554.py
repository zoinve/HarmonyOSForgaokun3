"""Run the ten original/new restricted-reader checks with ASan and UBSan."""
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'test-live-radio-reader-552.py').read_text()
    old="['cc','-O2','-Wall'"
    assert source.count(old)==1
    source=source.replace(old,"['cc','-O1','-g','-fsanitize=address,undefined','-Wall'",1)
    namespace=dict(__name__='radio554_tests',__file__=str(BASE/'test-live-radio-sanitizers-554.generated.py'))
    exec(compile(source,namespace['__file__'],'exec'),namespace)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(namespace['RadioReader'])
    result=unittest.TextTestRunner().run(suite)
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun==10 else 1)
