from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).parent


class ConfigPolicyObservation(unittest.TestCase):
    def test_only_original_parameter_reads_are_added(self):
        path = BASE / 'prepare-baremetal-sdk-original-init-082.py'
        self.assertTrue(path.exists(), 'missing passive configuration observer')
        module = runpy.run_path(str(path))
        source = module['source']
        self.assertIn('const.cust.config_dir_layer', source)
        self.assertIn('const.cust.follow_x_rules', source)
        self.assertIn('"/system/bin/param", "get",', source)
        self.assertNotIn('"/system/bin/param", "set",', source)
        self.assertIn('alarm(8)', source)
        compile(module['payload'], 'offline-config-policy-build', 'exec')

    def test_new_run_and_verifier_preserve_existing_checks(self):
        for name, key in [('run-baremetal-sdk-original-init-082.py', 'payload'),
                          ('verify-original-graphics-boot-082.py', 'source')]:
            self.assertTrue((BASE / name).exists(), name)
            module = runpy.run_path(str(BASE / name))
            compile(module[key], 'offline-config-policy-adapter', 'exec')
        verifier = runpy.run_path(str(BASE / 'verify-original-graphics-boot-082.py'))['source']
        self.assertIn('original_config_parameter_results', verifier)
        self.assertIn('original_config_parameter_output', verifier)
        self.assertIn('physical_board_test=False', verifier)


if __name__ == '__main__':
    unittest.main()
