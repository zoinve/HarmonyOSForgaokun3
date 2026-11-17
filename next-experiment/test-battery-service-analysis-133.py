from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent
correlate = runpy.run_path(str(BASE / 'analyze-battery-service-133.py'))['correlate']


class ServiceAnalysisTests(unittest.TestCase):
    def fixture(self):
        values = dict(type='Battery', capacity='98', present='1', current_now='0', voltage_now='8296000')
        return dict(samples=[dict(path='/sys/class/power_supply/battery',
                                 attributes={key: dict(valid=True, value=value) for key, value in values.items()})],
                    original_battery_consumer_records=[dict(line=5, fields=dict(capacity='98', present='1', currNow='0', voltage='8296000'))],
                    original_mock_path_records=[])

    def test_four_measured_fields_plus_original_real_root(self):
        analysis = self.fixture()
        log = 'power_host/BatteryInfo: read path(/sys/class/power_supply//temp) failed, ret: -17'
        self.assertTrue(correlate(analysis, log)['genuine_battery_service_data_correlated'])
        self.assertFalse(correlate(analysis, '')['genuine_battery_service_data_correlated'])
        analysis['original_mock_path_records'] = [dict(line=1, text='mock')]
        self.assertFalse(correlate(analysis, log)['genuine_battery_service_data_correlated'])

    def test_absent_or_mismatched_fields_do_not_pass(self):
        log = 'power_host/BatteryInfo: read path(/sys/class/power_supply//health) failed, ret: -17'
        for key in ['voltage', 'currNow', 'present', 'capacity']:
            analysis = self.fixture()
            analysis['original_battery_consumer_records'][0]['fields'].pop(key)
            self.assertFalse(correlate(analysis, log)['genuine_battery_service_data_correlated'])
        analysis = self.fixture()
        analysis['original_battery_consumer_records'][0]['fields']['capacity'] = '11'
        self.assertFalse(correlate(analysis, log)['genuine_battery_service_data_correlated'])


if __name__ == '__main__':
    unittest.main()
