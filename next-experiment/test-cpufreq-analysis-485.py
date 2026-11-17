"""Positive and negative fixture coverage for real-native evidence labels."""
from pathlib import Path
import io
import runpy
import unittest

ANALYSIS = runpy.run_path(str(Path(__file__).with_name('analyze-cpufreq-native-484.py')))


class AnalysisTest(unittest.TestCase):
    def inspect(self, text):
        return ANALYSIS['phase_inspect'](io.BytesIO(text.encode()))

    def test_only_real_complete_policy_counts(self):
        text = '''PHASE_END cpufreq-icc-provider-471 status=0
CPUFREQ471_BEGIN_REAL_SYSFS
POLICY=/sys/devices/system/cpu/cpufreq/policy0
ATTRIBUTE=scaling_driver
qcom-cpufreq-hw
ATTRIBUTE=related_cpus
0 1 2 3
ATTRIBUTE=scaling_cur_freq
1000000
ATTRIBUTE=scaling_min_freq
300000
ATTRIBUTE=scaling_max_freq
2438400
CPUFREQ471_END_NOT_TASK_MANAGER_ACCEPTANCE
'''
        result = self.inspect(text)
        self.assertEqual(result['provider_load_statuses'], [0])
        self.assertEqual(result['complete_policy_names'], ['policy0'])
        self.assertFalse(result['task_manager_ui_verified'])
        for corrupt in (text.replace('1000000', '0'), text.replace('qcom-cpufreq-hw\n', 'unknown\n'),
                        text.replace('300000\n', 'cat: missing\n')):
            self.assertFalse(self.inspect(corrupt)['real_native_cpufreq_policies_observed'])

    def test_failure_and_original_reader_not_hidden(self):
        result = self.inspect('PHASE_END cpufreq-icc-provider-471 status=1\n18591000.cpufreq qcom-cpufreq-hw: Failed to find icc paths\ncpu0, cpuFreq=0, minFreq=0, maxFreq=0\n')
        self.assertEqual(result['provider_load_statuses'], [1])
        self.assertEqual(result['missing_icc_deferred_probe_lines'], [2])
        self.assertFalse(result['real_native_cpufreq_policies_observed'])
        errors = ANALYSIS['reader_inspect'](io.BytesIO(b'GetIntegerFromFile: failed to get content from file=/sys/devices/system/cpu/cpu3/cpufreq/scaling_cur_freq\n'))
        self.assertEqual(errors['original_frequency_reader_error_count'], 1)


if __name__ == '__main__':
    unittest.main()
