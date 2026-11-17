from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent
summarize = runpy.run_path(str(BASE / 'analyze-native-drivers-133.py'))['summarize']


def measurement(stage, path, attributes):
    return '\n'.join('GAOKUN_DRIVER133 stage=' + stage + ' mono_ms=1234 path=' + path +
                     ' attr=' + name + ' valid=1 value=' + value for name, value in attributes.items())


class AnalysisTests(unittest.TestCase):
    def test_real_consumer_and_backlight_readback(self):
        phase = measurement('before_services', '/sys/class/backlight/ae96000.dsi.0',
                            dict(brightness='512', actual_brightness='512', max_brightness='4095'))
        phase += '\n' + measurement('services_sample', '/sys/class/backlight/ae96000.dsi.0',
                                    dict(brightness='710', actual_brightness='710', max_brightness='4095'))
        phase += '\n' + measurement('services_sample', '/sys/class/power_supply/battery',
                                    dict(type='Battery', capacity='98', present='1', current_now='0'))
        hilog = ('I power_host/BatteryInfo: system battery path is exist\n'
                 'I powermgr/BatteryInfo: capacity=98, present=1, currNow=0, temperature=0\n'
                 'I render_service/RSScreen: SetScreenBacklight id: 0, level is 11363, current level is 8194')
        result = summarize(phase, hilog)
        self.assertTrue(result['genuine_battery_consumption_observed'])
        self.assertTrue(result['backlight_hardware_readback_correlated'])
        self.assertFalse(result['temperature_measured'])
        for key in ['physical_luminance_verified', 'brightness_slider_verified', 'battery_ui_verified',
                    'unplug_replug_verified', 'suspend_resume_verified']:
            self.assertFalse(result[key])

    def test_mock_or_missing_fields_cannot_pass(self):
        phase = measurement('services_sample', '/sys/class/power_supply/battery',
                            dict(type='Battery', capacity='98', present='1'))
        hilog = ('power_host/BatteryInfo: system battery path is exist\n'
                 'powermgr/BatteryInfo: capacity=98, present=1\n')
        self.assertFalse(summarize(phase, hilog)['genuine_battery_consumption_observed'])
        phase += '\n' + measurement('services_sample', '/sys/class/power_supply/battery', dict(current_now='0'))
        hilog = hilog.replace('present=1', 'present=1, currNow=0')
        self.assertTrue(summarize(phase, hilog)['genuine_battery_consumption_observed'])
        hilog += '\npower_host/BatteryInfo: create mockFilePath path'
        self.assertFalse(summarize(phase, hilog)['genuine_battery_consumption_observed'])

    def test_readback_without_transition_or_request_cannot_pass(self):
        phase = measurement('services_sample', '/sys/class/backlight/ae96000.dsi.0',
                            dict(brightness='710', actual_brightness='710', max_brightness='4095'))
        hilog = 'SetScreenBacklight id: 0, level is 11363'
        self.assertFalse(summarize(phase, hilog)['backlight_hardware_readback_correlated'])
        phase += '\n' + measurement('before_services', '/sys/class/backlight/ae96000.dsi.0', dict(brightness='512'))
        self.assertFalse(summarize(phase, '')['backlight_hardware_readback_correlated'])
        phase = phase.replace('actual_brightness valid=1 value=710', 'actual_brightness valid=1 value=700')
        self.assertFalse(summarize(phase, hilog)['backlight_hardware_readback_correlated'])


if __name__ == '__main__':
    unittest.main()
