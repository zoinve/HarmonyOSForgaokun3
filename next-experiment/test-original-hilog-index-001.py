"""Offline gates for a genuine, query-child-only logging-index mount."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve().parent


class QueryIndexTests(unittest.TestCase):
    def test_observation_verifier_keeps_original_identity_gates(self):
        path = HERE / 'verify-original-graphics-boot-066.py'
        self.assertTrue(path.exists(), 'missing screen/dictionary evidence verifier')
        source = runpy.run_path(str(path))['source']
        self.assertIn('extract_process_pids', source)
        self.assertIn('observed_dictionary_files', source)
        self.assertIn('screen_dump_wait_statuses', source)
        self.assertIn('readiness_verified=False', source)
        self.assertNotIn("entries['graphics-dict-info.json']", source)
        compile(source, 'observation-evidence-066', 'exec')

    def test_screen_observation_runner_keeps_the_same_graphics_bundle(self):
        path = HERE / 'run-baremetal-sdk-original-init-066.py'
        self.assertTrue(path.exists(), 'missing observation runner')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('original-graphics-egl-009/result.json', payload)
        self.assertIn('harmony-sdk-qemu066-', payload)
        self.assertIn('original-init-066/result.json', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertNotIn('graphics-dict-info.json', payload)
        compile(payload, 'screen-observation-runner', 'exec')

    def test_next_query_observes_real_dictionary_and_original_screen_dump(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-066.py'
        self.assertTrue(path.exists(), 'missing real dictionary observation fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('/data/log/dict/2C/EB723E313C80C3605ECD369C0B8CB6', source)
        self.assertIn('GRAPHICS066_DICT_FILE', source)
        self.assertIn('GRAPHICS066_SCREEN_DUMP', source)
        self.assertIn('"/system/bin/hidumper", "-s", "RenderService", "-a", "screen"', source)
        self.assertNotIn('/graphics-dict-info.json', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertIn('execv(args[0], args)', source)

    def test_index_mount_is_in_query_child_not_original_services(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-065.py'
        self.assertTrue(path.exists(), 'missing private-query fixture')
        source = runpy.run_path(str(path))['source']
        child = source[source.index('if (log_child == 0)'):source.index('if (log_child > 0)')]
        self.assertIn('unshare(CLONE_NEWNS)', child)
        self.assertIn('MS_REC | MS_PRIVATE', child)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY', child)
        self.assertIn('/graphics-dict-info.json', child)
        self.assertIn('/log/hilog/.dict_info.json', child)
        self.assertIn('execv(args[0], args)', child)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertNotIn('setparam ', child)
        self.assertIn('alarm(12)', child)

    def test_runner_pins_genuine_cache_and_unchanged_graphics(self):
        path = HERE / 'run-baremetal-sdk-original-init-065.py'
        self.assertTrue(path.exists(), 'missing numbered runner')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('d8b36a8aca5c9adfd610395ba9de0368f782e475f7ae7d1be8241e8db8e5f50a', payload)
        self.assertIn('2CEB723E313C80C3605ECD369C0B8CB6', payload)
        self.assertIn('original-graphics-egl-009/result.json', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn("'-smp','8'", payload)
        self.assertIn("'-m','4096'", payload)
        self.assertNotIn("'setenforce'", payload)
        compile(payload, 'query-index-065', 'exec')

    def test_verifier_checks_injected_index_and_records_actual_decode_outcome(self):
        path = HERE / 'verify-original-graphics-boot-065.py'
        self.assertTrue(path.exists(), 'missing independent verifier')
        source = runpy.run_path(str(path))['source']
        self.assertIn("entries['graphics-dict-info.json'][1]", source)
        self.assertIn('decoded_original_hilog_lines', source)
        self.assertIn('private_index_mounts_observed', source)
        self.assertIn('readiness_verified=False', source)
        compile(source, 'independent-query-index-065', 'exec')

    def test_process_parser_ignores_console_text_after_actual_command(self):
        path = HERE / 'original-graphics-process-records-001.py'
        self.assertTrue(path.exists(), 'missing command-token parser')
        parse = runpy.run_path(str(path))['extract_process_pids']
        raw = (b'GRAPHICS065_PROCESS sample=12 pid=684 cmd=foundation [ 83.4] denied comm="allocator_host"\n'
               b'GRAPHICS065_PROCESS sample=12 pid=944 cmd=allocator_host -i 12 -n allocator_host\n'
               b'GRAPHICS065_PROCESS sample=12 pid=675 cmd=/system/bin/render_service [ 84.5] unrelated\n')
        self.assertEqual(parse(raw, b'GRAPHICS065_', 'allocator_host'), [944])
        self.assertEqual(parse(raw, b'GRAPHICS065_', 'render_service'), [675])


if __name__ == '__main__':
    unittest.main()
