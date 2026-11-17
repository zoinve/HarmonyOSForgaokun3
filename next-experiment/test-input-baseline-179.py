"""Reject cross-sample identity joins and incomplete observations."""
from pathlib import Path
import runpy
import unittest

API = runpy.run_path(str(Path(__file__).with_name('analyze-input-baseline-179.py')))


def sample(body='',stage='test',stamp=1,end=True):
    return ('INPUTUSB148_OBSERVE_BEGIN stage='+stage+' mono_ms='+str(stamp)+' read_only=1 input_events_read=0\n'
        +body+'\n'+('INPUTUSB148_OBSERVE_END stage='+stage+' physical_interaction_acceptance_not_inferred=1\n' if end else ''))


TOUCH = 'GAOKUN_DRIVER133 stage=test mono_ms=1 path=/sys/class/input/event2/device attr=name valid=1 value=Himax Capacitive TouchScreen'
FD = 'INPUTUSB148_SERVICE_FD stage=test pid=44 name=multimodalinput fd=23 node=/dev/input/event2'


class BaselineTests(unittest.TestCase):
    def test_same_sample_matches(self):
        row = API['summarize'](sample(TOUCH+'\n'+FD))
        self.assertTrue(row['native_mmi_holds_touchscreen'])
        self.assertFalse(row['physical_touch_accuracy_verified'])

    def test_cross_sample_fd_not_joined(self):
        row = API['summarize'](sample(TOUCH)+sample(FD,stamp=2))
        self.assertFalse(row['native_mmi_holds_touchscreen'])

    def test_incomplete_not_accepted(self):
        row = API['summarize'](sample(TOUCH+'\n'+FD,end=False))
        self.assertFalse(row['native_mmi_holds_touchscreen'])
        self.assertEqual(row['incomplete_or_mismatched_samples'],1)

    def test_mismatched_end_not_accepted(self):
        text=sample(TOUCH+'\n'+FD).replace('OBSERVE_END stage=test','OBSERVE_END stage=other')
        self.assertFalse(API['summarize'](text)['native_mmi_holds_touchscreen'])

    def test_wrong_stage_or_timestamp_ignored(self):
        for touch in [TOUCH.replace('stage=test','stage=other'),TOUCH.replace('mono_ms=1','mono_ms=2')]:
            self.assertFalse(API['summarize'](sample(touch+'\n'+FD))['native_mmi_holds_touchscreen'])

    def test_module_states_not_combined_across_samples(self):
        body=lambda module:'GAOKUN_DRIVER133 stage=test mono_ms=1 path=/sys/module/'+module+' attr=initstate valid=1 value=live'
        row=API['summarize'](''.join(sample(body(module)) for module in ['usb_storage','uas','exfat']))
        self.assertFalse(row['storage_modules_live_together'])
        row=API['summarize'](sample('\n'.join(body(module) for module in ['usb_storage','uas','exfat'])))
        self.assertTrue(row['storage_modules_live_together'])


if __name__ == '__main__':
    unittest.main()
