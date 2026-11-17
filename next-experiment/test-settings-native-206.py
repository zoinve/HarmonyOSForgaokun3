"""Test real gate branches and preserve the single-launch latch for aa exit75."""
from pathlib import Path
import ast
import re
import runpy
import subprocess
import unittest

BASE=Path(__file__).resolve().parent
source=(BASE/'test-settings-native-205.py').read_text().replace('205','206')
namespace={'__name__':'settings206_cases','__file__':str(__file__)}
exec(compile(source,str(__file__),'exec'),namespace)
Settings206Tests=namespace['Settings206Tests']


class ReservedExitTests(unittest.TestCase):
    def test_original_aa_exit75_does_not_reopen_launch_gate(self):
        api=runpy.run_path(str(BASE/'settings-native-206.py'))
        fragment=api['header206']().split('static const char script[] =',1)[1].split('char *const args[]',1)[0]
        script=''.join(ast.literal_eval(text) for text in re.findall(r'"(?:[^"\\]|\\.)*"',fragment))
        script=script.replace('/system/bin/param get $1','printf true')
        original='/system/bin/aa start -b com.huawei.hmos.settings -a com.huawei.hmos.settings.MainAbility -m pc_settings'
        for status,expected in [(0,0),(1,1),(75,76),(76,76),(126,126)]:
            fixture=script.replace(original,'(exit '+str(status)+')')
            result=subprocess.run(['/bin/sh','-c',fixture],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,expected,result.stderr)
            self.assertNotEqual(result.returncode,75)
            self.assertEqual(result.stdout.count('SETTINGS206_REQUEST '),1)


if __name__=='__main__':unittest.main()
