"""Check exact native delta and execute all readiness branches without target access."""
from pathlib import Path
import ast
import json
import os
import re
import runpy
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
API=runpy.run_path(str(BASE/'settings-native-205.py'))


class Settings205Tests(unittest.TestCase):
    def test_readiness_shell_branches(self):
        header=API['header205']()
        fragment=header.split('static const char script[] =',1)[1].split('char *const args[]',1)[0]
        script=''.join(ast.literal_eval(text) for text in re.findall(r'"(?:[^"\\]|\\.)*"',fragment))
        with tempfile.TemporaryDirectory(prefix='settings205-') as directory:
            root=Path(directory)
            param=root/'param';aa=root/'aa'
            param.write_text('#!/bin/sh\ncase $2 in\nbootevent.bms.main.bundles.ready) echo ${BMS:-};;\nbootevent.account.ready) echo ${ACCOUNT:-};;\nbootevent.appfwk.ready) echo ${APPFWK:-};;\nesac\n')
            aa.write_text('#!/bin/sh\nprintf "ORIGINAL_AA_FIXTURE %s\\n" "$*"\n')
            param.chmod(0o700);aa.chmod(0o700)
            fixture=script.replace('/system/bin/param',str(param)).replace('/system/bin/aa',str(aa))
            for bms,account,appfwk,accepted in [('', '', '', False),('true','false','true',False),
                ('false','true','true',False),('true','true','false',False),
                ('true-not-ready','true','true',False),('true','true','true',True)]:
                proc=subprocess.run(['/bin/sh','-c',fixture],env=dict(os.environ,BMS=bms,ACCOUNT=account,APPFWK=appfwk),
                    capture_output=True,text=True,timeout=5)
                self.assertEqual(proc.returncode,0 if accepted else 75,proc.stderr)
                self.assertEqual(proc.stdout.count('SETTINGS205_REQUEST '),int(accepted))
                self.assertEqual(proc.stdout.count('ORIGINAL_AA_FIXTURE '),int(accepted))
                self.assertIn('original_parameters_read_only=1',proc.stdout)
                if accepted:self.assertIn('-m pc_settings',proc.stdout)

    def test_native_guards_and_exact_source(self):
        work=BUILD/'commercial61-native-205';parent=BUILD/'commercial61-native-201'
        source=(work/'init.c').read_text()
        self.assertEqual(source,API['outer205']((parent/'init.c').read_text()))
        header=API['header205']()
        self.assertEqual(header,(work/'settings-launch-205.h').read_text())
        self.assertIn('if (result != 75) { attempted=1;',header)
        self.assertNotIn('active_user_selected_by_original_ams=1',header)
        for name in ['bootstrap-runtime087','bootstrap-runtime087.c','persistent-data-166.h',
                     'persistent-data-172.h','persistent-unmount-plan-201.h']:
            self.assertEqual((work/name).read_bytes(),(parent/name).read_bytes())
        for required in ['O_EXCL','SYS_pidfd_open','PR_SET_PDEATHSIG','8000','makedev(7,3)']:
            self.assertIn(required,header)
        for forbidden in ['setuid(', 'setgid(', 'capset(', 'param set', 'force-stop', 'switch -i', 'LD_PRELOAD']:
            self.assertNotIn(forbidden,header)
        self.assertIn('unsigned left033=900;',source)
        self.assertIn('elapsed033<720',source)
        info=json.loads((work/'result.json').read_text())['settings205']
        self.assertEqual(info['maximum_application_launch_requests'],1)
        self.assertEqual(info['expected_preboot_candidate_sha256'],API['EXPECTED_DATA'])


if __name__=='__main__':unittest.main()
