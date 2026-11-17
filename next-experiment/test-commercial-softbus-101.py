"""Check the precise reference-scoped service delta before building candidate 101."""
from pathlib import Path
import copy
import json
import runpy
import subprocess
import unittest

BASE = Path(__file__).resolve().parent
BUILDER = runpy.run_path(str(BASE/'build-commercial-native-101.py'))
AUDIT = json.loads((BASE.parent/'reports/desktop-dispatch-audit-100/softbus-reference-comparison.json').read_text())


class SoftBusTests(unittest.TestCase):
    def config(self):
        return dict(jobs=[dict(name='post-fs-data', cmds=['mkdir /data/example'])],
                    services=[copy.deepcopy(AUDIT['source_service']), dict(name='unrelated', uid='system')])

    def test_only_exact_env_removed(self):
        original = self.config()
        updated = json.loads(BUILDER['adapt_config'](json.dumps(original).encode()))
        self.assertEqual(updated['services'][0]['env'], [])
        updated['services'][0]['env'] = original['services'][0]['env']
        self.assertEqual(updated, original)

    def test_other_env_preserved(self):
        original = self.config()
        original['services'][0]['env'].append(dict(name='EXAMPLE', value='kept'))
        updated = json.loads(BUILDER['adapt_config'](json.dumps(original).encode()))
        self.assertEqual(updated['services'][0]['env'], [dict(name='EXAMPLE', value='kept')])

    def test_missing_preload_refused(self):
        original = self.config()
        original['services'][0]['env'] = []
        with self.assertRaises(AssertionError):
            BUILDER['adapt_config'](json.dumps(original).encode())

    def test_duplicate_preload_refused(self):
        original = self.config()
        original['services'][0]['env'] *= 2
        with self.assertRaises(AssertionError):
            BUILDER['adapt_config'](json.dumps(original).encode())

    def test_duplicate_service_refused(self):
        original = self.config()
        original['services'].append(original['services'][0])
        with self.assertRaises(AssertionError):
            BUILDER['adapt_config'](json.dumps(original).encode())

    def test_runtime_patch_precise(self):
        parent = (BUILDER['BUILD']/'commercial61-native-099/bootstrap-runtime087.c').read_text()
        actual = BUILDER['inner_source'](parent, '0'*64)
        addition = ('    commercial_copy005("/softbus-reference101.cfg","/run/commercial-system005/upper/etc/init/softbus_server_musl.cfg",0644);\n'
                    '    dprintf(1,"SOFTBUS101_RAM_CONFIG sha256='+'0'*64+' stock_service_permissions_unchanged=1 platform_ble_preload_removed=1\\n");\n')
        self.assertEqual(actual.replace(addition, '', 1), parent)
        self.assertEqual(actual.count(addition), 1)

    def test_unknown_runtime_refused(self):
        with self.assertRaises(AssertionError):
            BUILDER['inner_source']('not the sealed bootstrap', '0'*64)

    def test_observer_read_only(self):
        observer = (BASE/'commercial-softbus-observer-101.sh').read_text()
        for forbidden in ('force-stop', 'kill ', 'param set', 'begetctl', 'LD_PRELOAD=', 'environ', 'settings put'):
            self.assertNotIn(forbidden, observer)
        subprocess.run(['/bin/sh', '-n', str(BASE/'commercial-softbus-observer-101.sh')], check=True)


if __name__ == '__main__':
    unittest.main()
