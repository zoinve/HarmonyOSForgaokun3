from pathlib import Path
import runpy
import unittest

summarize = runpy.run_path(str(Path(__file__).with_name('analyze-input-usb-148.py')))['summarize']


class AnalysisTests(unittest.TestCase):
    def test_metadata_is_not_physical_acceptance(self):
        data = summarize('''INPUTUSB148_MODULE_RESULT module=uas status=0 storage_acceptance_not_inferred=1
INPUTUSB148_OBSERVE_BEGIN stage=services_sample148 mono_ms=40000 read_only=1 input_events_read=0
GAOKUN_DRIVER133 stage=services_sample148 mono_ms=40000 path=/sys/class/input/event77/device attr=name valid=1 value=Himax Capacitive TouchScreen
INPUTUSB148_AXIS stage=services_sample148 node=/dev/input/event77 code=53 min=0 max=2559 fuzz=0 flat=0 resolution=0
INPUTUSB148_SERVICE_FD stage=services_sample148 pid=21 name=multimodalinput fd=31 node=/dev/input/event77
GAOKUN_DRIVER133 stage=services_sample148 mono_ms=40000 path=/sys/module/usb_storage attr=initstate valid=1 value=live
GAOKUN_DRIVER133 stage=services_sample148 mono_ms=40000 path=/sys/module/uas attr=initstate valid=1 value=live
GAOKUN_DRIVER133 stage=services_sample148 mono_ms=40000 path=/sys/module/exfat attr=initstate valid=1 value=live
INPUTUSB148_OBSERVE_END stage=services_sample148 physical_interaction_acceptance_not_inferred=1
''')
        self.assertTrue(data['native_mmi_holds_touchscreen'])
        self.assertTrue(data['storage_modules_live'])
        self.assertEqual(data['touchscreen_samples'][0]['axes']['53']['maximum'], 2559)
        self.assertFalse(data['physical_touch_accuracy_verified'])
        self.assertFalse(data['usb_storage_file_access_verified'])

    def test_missing_and_incomplete_evidence_not_success(self):
        data = summarize('INPUTUSB148_OBSERVE_BEGIN stage=test mono_ms=0 read_only=1 input_events_read=0\n')
        self.assertFalse(data['samples'][0]['completed'])
        self.assertFalse(data['native_mmi_holds_touchscreen'])
        self.assertFalse(data['storage_modules_live'])

    def test_current_entrypoint_rejects_cross_sample_and_incomplete_joins(self):
        api = runpy.run_path(str(Path(__file__).with_name('test-input-baseline-179.py')))
        sample, touch, fd = api['sample'], api['TOUCH'], api['FD']
        self.assertFalse(summarize(sample(touch)+sample(fd,stamp=2))['native_mmi_holds_touchscreen'])
        self.assertFalse(summarize(sample(touch+'\n'+fd,end=False))['native_mmi_holds_touchscreen'])
        self.assertFalse(summarize(sample(touch+'\n'+fd).replace('OBSERVE_END stage=test',
            'OBSERVE_END stage=other'))['native_mmi_holds_touchscreen'])

    def test_module_states_must_share_complete_sample(self):
        def sample(module):
            return ('INPUTUSB148_OBSERVE_BEGIN stage=test mono_ms=1 read_only=1 input_events_read=0\n'
                'GAOKUN_DRIVER133 stage=test mono_ms=1 path=/sys/module/'+module+' attr=initstate valid=1 value=live\n'
                'INPUTUSB148_OBSERVE_END stage=test physical_interaction_acceptance_not_inferred=1\n')
        self.assertFalse(summarize(''.join(sample(module) for module in ['usb_storage','uas','exfat']))['storage_modules_live'])


if __name__ == '__main__':
    unittest.main()
