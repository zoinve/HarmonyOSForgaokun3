'''Compile real outer code and verify diagnostic-only planner transformations.'''
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE=Path(__file__).resolve().parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
ADAPT=runpy.run_path(str(BASE/'settings-native-201.py'))


class SettingsNativeTests(unittest.TestCase):
    def test_planner_acceptance_and_diagnostic_reasons(self):
        harness=runpy.run_path(str(BASE/'test-persistent-lifecycle-172.py'))['HARNESS']
        harness=harness.replace('persistent-unmount-plan-172.h','persistent-unmount-plan-201.h')
        anchor='  puts("planner cases passed");return 0;'
        assert harness.count(anchor)==1
        extra=r'''
  assert(plan("1 0 0:1 / / rw - tmpfs tmpfs rw",&count) && persistent201_plan_reason==1);
  assert(plan("broken\n",&count) && persistent201_plan_reason==3);
  assert(plan("0 0 0:1 / / rw - tmpfs tmpfs rw\n",&count) && persistent201_plan_reason==4);
  assert(plan("1 0 0:1 / / rw missing separator\n",&count) && persistent201_plan_reason==5);
  assert(plan("1 0 0:1 / /bad\\999 rw - tmpfs tmpfs rw\n",&count) && persistent201_plan_reason==6);
  assert(plan("1 0 0:1 / / rw - tmpfs tmpfs rw\n1 0 0:2 / /x rw - tmpfs tmpfs rw\n",&count) && persistent201_plan_reason==7);
  assert(plan("",&count) && persistent201_plan_reason==9);
  assert(plan("1 0 7:3 / / rw - ext4 loop rw\n",&count) && persistent201_plan_reason==10);
  assert(plan("1 0 0:1 / / rw - tmpfs tmpfs rw\n2 1 7:3 / /data rw - ext4 loop rw\n3 1 0:2 / /data rw - tmpfs tmpfs rw\n",&count) && persistent201_plan_reason==11);
'''
        harness=harness.replace(anchor,extra+anchor,1)
        with tempfile.TemporaryDirectory(prefix='settings-plan201-') as directory:
            root=Path(directory)
            (root/'persistent-unmount-plan-201.h').write_text(ADAPT['plan201']((BASE/'persistent-unmount-plan-172.h').read_text()))
            (root/'test.c').write_text(harness)
            proc=subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror',str(root/'test.c'),'-o',str(root/'test')],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            proc=subprocess.run([str(root/'test')],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            for reason in [1,3,4,5,6,7,9,10,11]:
                self.assertIn('PERSISTENT201_PLAN_REFUSED reason='+str(reason)+' ',proc.stdout)

    def test_actual_outer_source_and_unchanged_desktop_runtime(self):
        work=BUILD/'commercial61-native-201';parent=BUILD/'commercial61-native-197-r1'
        self.assertEqual((work/'init.c').read_text(),ADAPT['outer201']((parent/'init.c').read_text()))
        self.assertEqual((work/'persistent-data-172.h').read_text(),ADAPT['lifecycle201']((BASE/'persistent-data-172.h').read_text()))
        self.assertEqual((work/'persistent-data-166.h').read_bytes(),(parent/'persistent-data-166.h').read_bytes())
        for name in ['bootstrap-runtime087','bootstrap-runtime087.c']:
            self.assertEqual((work/name).read_bytes(),(parent/name).read_bytes())
        self.assertEqual((work/'init.c').read_text().count('if(i==10)settings201_start(child);'),1)

    def test_fixed_original_cli_and_guards(self):
        text=(BASE/'settings-launch-201.h').read_text()
        for required in ['"/system/bin/aa","start"','"com.huawei.hmos.settings.MainAbility"',
                         '"pc_settings"','PR_SET_PDEATHSIG','SYS_pidfd_open','CLONE_NEWPID',
                         'st_dev != makedev(7,3)','8000','O_EXCL','credentials_unmodified=1']:
            self.assertIn(required,text)
        for forbidden in ['setuid(', 'setgid(', 'capset(', 'LD_PRELOAD', 'force-stop', 'sh -c', 'com.huawei.hmos.pcsettings']:
            self.assertNotIn(forbidden,text)
        lifecycle=ADAPT['lifecycle201']((BASE/'persistent-data-172.h').read_text())
        for forbidden in ['MNT_DETACH','MNT_FORCE','ftruncate(', 'unlink(', 'system(', 'chmod(']:
            self.assertNotIn(forbidden,lifecycle)


if __name__=='__main__':unittest.main()
