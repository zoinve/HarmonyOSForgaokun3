"""Offline ordering/argv tests; not a successful target desktop claim."""
from pathlib import Path
import runpy, unittest

base=Path(__file__).resolve().parent
assert (base/'commercial-desktop-order-020.py').is_file(), 'missing reference-aligned desktop ordering repair'
repair=runpy.run_path(str(base/'commercial-desktop-order-020.py'))['repair']
wait='''checks=0
while [ "$checks" -lt 30 ]; do
    [ "$(read_param bootevent.account.ready)" = true ] && break
    checks=$((checks + 1))
    /system/bin/sleep 1
done
'''
tail='''if [ "$(read_param bootevent.account.ready)" = true ] && \\
   [ "$(read_param bootevent.wms.ready)" != true ]; then
    /usr/bin/aa start \\
        -b com.ohos.sceneboard \\
        -a com.ohos.sceneboard.MainAbility \\
        -m pc_sceneboard
fi
'''
original='#!/system/bin/sh\nset -u\n# unchanged HUKS and stock account-service ordering\n'+wait+'# unchanged framework readiness wait\n'+tail

class Tests(unittest.TestCase):
    def test_only_circular_wait_and_final_launch_gate_change(self):
        new=repair(original)
        self.assertTrue(new.startswith(original[:original.index(wait)]))
        self.assertIn('# unchanged framework readiness wait',new)
        self.assertNotIn('read_param bootevent.account.ready',new)
        self.assertIn('read_param bootevent.appfwk.ready',new)
        self.assertIn('read_param bootevent.bms.main.bundles.ready',new)
        self.assertIn('/usr/bin/aa start',new)
        self.assertIn('-m pc_sceneboard -u 100',new)
        self.assertIn('/system/bin/pidof com.ohos.sceneboard',new)
        self.assertNotIn('force-stop',new)
        for forbidden in ['param set','setuid','setgid','LD_PRELOAD','sandbox-switch off']:
            self.assertNotIn(forbidden,new)
        with self.assertRaises(AssertionError): repair(new)

if __name__=='__main__': unittest.main()
