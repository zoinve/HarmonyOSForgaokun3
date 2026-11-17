from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-probes-085.py')))['analyze']


def phase(mode, code=0, context='11 22 33 44', tls='0', http='204'):
    pid, net, mnt, ns = context.split()
    body = f'NETWORK084_TARGET_CONTEXT pid={pid} net_inode={net} mnt_inode={mnt} pid_inode={ns} root_verified=1 mode={mode} connectivity_not_inferred=1\n'
    if mode in ('http', 'https'):
        body += f'NETWORK085_PROBE mode={mode} original_curl=1 tls_bypass=0 success_not_inferred=1\n'
        body += f'NETWORK085_CURL http_code={http} remote_ip=192.0.2.5 namelookup=0.02 ssl_verify_result={tls}\n'
    return f'PHASE_BEGIN wifi-supplicant-{mode}085\n{body}PHASE_END wifi-supplicant-{mode}085 status={code}\n'


class ProbeTests(unittest.TestCase):
    def result(self, probe, start=True):
        return analyze('NETWORK084_PRIVATE_CONFIG_VERIFIED_RAM_ONLY\n' + (phase('start') if start else '') + probe)

    def test_actual_success_requires_completed_phase_and_context(self):
        self.assertTrue(self.result(phase('https'))['independent_https_204_tls_verification_proven'])
        self.assertTrue(self.result(phase('http'))['independent_http_204_proven'])

    def test_nonzero_exit_never_proves_success(self):
        self.assertFalse(self.result(phase('https', code=60))['independent_https_204_tls_verification_proven'])

    def test_tls_failure_never_proves_https(self):
        self.assertFalse(self.result(phase('https', tls='20'))['independent_https_204_tls_verification_proven'])

    def test_missing_or_wrong_target_context_refused(self):
        self.assertFalse(self.result(phase('https'), start=False)['independent_https_204_tls_verification_proven'])
        self.assertFalse(self.result(phase('https', context='11 99 33 44'))['independent_https_204_tls_verification_proven'])

    def test_wrong_response_or_incomplete_phase_refused(self):
        self.assertFalse(self.result(phase('https', http='302'))['independent_https_204_tls_verification_proven'])
        self.assertFalse(self.result(phase('https').split('PHASE_END')[0])['independent_https_204_tls_verification_proven'])

    def test_cumulative_duplicates_not_repeated_operations(self):
        self.assertEqual(len(self.result(phase('https') * 2)['probe_records']), 1)

    def test_working_network_not_desktop_proof(self):
        result = self.result(phase('https'))
        self.assertFalse(result['oobe_completed_proven'])
        self.assertFalse(result['desktop_visible_interaction_proven'])


if __name__ == '__main__':
    unittest.main()
