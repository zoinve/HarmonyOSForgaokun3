"""Validate read-only preset extraction against original bytecode evidence."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PresetEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ROOT / 'reports/commercial-dock-literals-audit-086-revision4/result.json').read_text())
        cls.objects = {item['index']: item for item in cls.result['literal_objects']}
        cls.methods = json.loads((ROOT / 'reports/commercial-dock-defaults-audit-086-revision3/decoded-methods.json').read_text())

    def test_original_identity(self):
        self.assertFalse(self.result['original_modified'])
        self.assertFalse(self.result['operational_boot_performed'])
        self.assertEqual(self.result['abc_sha256'], self.methods['abc_sha256'])
        self.assertEqual(self.result['bundle_name'], 'com.ohos.sceneboard')
        self.assertEqual(self.result['module_name'], 'pc_sceneboard')

    def test_literal_extents_match_next_original_object(self):
        ordered = sorted(self.objects.values(), key=lambda item: item['offset'])
        self.assertEqual(len(ordered), 15)
        for first, second in zip(ordered, ordered[1:]):
            self.assertEqual(first['offset'] + first['bytes'], second['offset'])

    def test_all_bytecode_object_operands_are_accounted_for(self):
        preset = next(m for m in self.methods['methods'] if '/PresetDockItem&' in m['record'])
        indices = [i['operands'][-1]['value'] for i in preset['instructions']
                   if i['name'] == 'createobjectwithbuffer']
        self.assertEqual(indices, [item['index'] for item in self.result['literal_objects']])

    def test_original_function_resources(self):
        self.assertEqual(self.objects[25982]['fields']['iconId'], '/common/pics/ic_allapps.png')
        self.assertEqual(self.objects[25984]['fields']['iconId'], '/common/pics/ic_multitask.png')
        for index in (25983, 25985):
            value = self.objects[index]['fields']
            self.assertEqual(value['bundleName'], self.result['bundle_name'])
            self.assertEqual(value['moduleName'], self.result['module_name'])
            self.assertEqual(value['type'], 10003)
            self.assertIsInstance(value['id'], int)

    def test_appgallery_is_original_default_not_installed_evidence(self):
        self.assertEqual(self.objects[25980]['fields']['bundleName'], 'com.huawei.hmsapp.appgallery')
        self.assertEqual(self.objects[25980]['fields']['abilityName'], 'com.huawei.hmsapp.appgallery.MainAbility')


if __name__ == '__main__':
    unittest.main()
