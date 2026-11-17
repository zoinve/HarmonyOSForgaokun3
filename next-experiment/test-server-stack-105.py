"""Reuse observer failure cases and verify DFX precedes the proc survey."""
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parent
source = (BASE/'test-server-stack-104.py').read_text().replace('104', '105')
anchor = "        self.assertIn('futex_wait_queue', log)"
assert source.count(anchor) == 1
source = source.replace(anchor, anchor+'''
        self.assertLess(log.index('APP_STACK_RESULT'), log.index('SERVER105_TASK tid='))
        self.assertLess(log.index('SERVER105_DFX_CALL_BEGIN'), log.index('APP_STACK_RESULT'))
        self.assertLess(log.index('SERVER105_CAPTURE_END'), log.index('SERVER105_TASK_SURVEY_BEGIN'))
''', 1)
if __name__ == '__main__':
    namespace = {'__name__': 'observer105_tests', '__file__': __file__}
    exec(compile(source, __file__, 'exec'), namespace)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(namespace['ObserverTests'])
    assert suite.countTestCases() == 6
    result = unittest.TextTestRunner().run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
