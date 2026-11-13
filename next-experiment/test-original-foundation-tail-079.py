"""Regress the real hilog -31 failure without rerunning completed experiments."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class FoundationTail(unittest.TestCase):
    def test_tail_is_the_only_command_in_the_foundation_query(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-079.py'
        self.assertTrue(path.exists(), 'missing corrected Foundation query')
        source = runpy.run_path(str(path))['source']
        start = source.index('static void graphics_foundation_query_078(')
        end = source.index('static void graphics_desktop_tool_077(', start)
        helper = source[start:end]
        self.assertIn('"/system/bin/hilog", "-z", "200", "-P"', helper)
        self.assertNotIn('"-x"', helper)
        self.assertIn('alarm(12)', helper)
        for text in ('setuid(', 'setcon(', 'setenforce(', 'force-stop'):
            self.assertNotIn(text, source)

    def test_runner_and_verifier_keep_original_graph_and_failures(self):
        runner = HERE / 'run-baremetal-sdk-original-init-079.py'
        verifier = HERE / 'verify-original-graphics-boot-079.py'
        self.assertTrue(runner.exists(), 'missing corrected-query runner')
        self.assertTrue(verifier.exists(), 'missing independent query verifier')
        payload = runpy.run_path(str(runner))['payload']
        for text in ('original-init-qemu-079', 'original-init-079/result.json',
                     'readonly=on', 'original-graphics-egl-009', 'original-graphics-provider-005'):
            self.assertIn(text, payload)
        module = runpy.run_path(str(verifier))
        self.assertIn('foundation_query_command_errors', module['source'])
        compile(module['source'], 'offline-foundation-tail-079', 'exec')


if __name__ == '__main__':
    unittest.main()
