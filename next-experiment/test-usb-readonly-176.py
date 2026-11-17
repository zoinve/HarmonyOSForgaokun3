"""Apply the exact175 guard tests through the operation-specific trace wrapper."""
from pathlib import Path

BASE=Path(__file__).resolve().parent

if __name__=='__main__':
    source=(BASE/'test-usb-readonly-175.py').read_text()
    assert source.count('#include "usb-readonly-175.h"')==1
    source=source.replace('#include "usb-readonly-175.h"','#include "usb-readonly-176.h"',1)
    anchor="if __name__ == '__main__':"
    extra='''    def test_guard_steps_are_numeric_and_distinguish_failure_site(self):
        result = subprocess.run([str(self.binary)], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        for stage in ['open', 'fstat', 'get_size', 'get_ro', 'set_ro']:
            self.assertIn('USB176_STEP stage=' + stage, result.stdout)
        self.assertIn('stage=open status=-1', result.stdout)
        self.assertIn('stage=fstat status=-1', result.stdout)
        self.assertIn('stage=set_ro status=-1', result.stdout)
        self.assertNotIn('PRIVATE_SERIAL', result.stdout)

'''
    assert source.count(anchor)==1
    source=source.replace(anchor,extra+anchor,1)
    assert source.count('    unittest.main()')==1
    source=source.replace('    unittest.main()',
        '    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ReadonlyTests)\n'
        '    assert suite.countTestCases()==4\n'
        '    result=unittest.TextTestRunner().run(suite)\n'
        '    raise SystemExit(not result.wasSuccessful())',1)
    exec(compile(source,'test-usb-readonly-176.generated.py','exec'),
         {'__name__':'__main__','__file__':str(BASE/'test-usb-readonly-176.generated.py')})
