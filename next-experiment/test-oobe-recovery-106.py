import runpy
from pathlib import Path
import unittest

events = runpy.run_path(str(Path(__file__).with_name('audit-oobe-recovery-106.py')))['events']


class RecoveryEventsTests(unittest.TestCase):
    def test_scene_filter(self):
        text = '\n'.join([
            '11-15 23:53:48.400  4878  4878 I C/tag: GetTrustedDeviceListWithAbilityFilter# end',
            '11-15 23:53:48.401  9999  9999 I C/tag: GetTrustedDeviceListWithAbilityFilter# end',
        ])
        found = events(text, 4878)
        self.assertEqual(len(found['query_end']), 1)
        self.assertEqual(found['query_end'][0]['milliseconds'], 86028400)

    def test_retains_duplicates_for_ambiguity_guard(self):
        line = '11-15 23:53:48.702  4878  4878 W C/tag: BaseOobeManager: start oobe again'
        self.assertEqual(len(events(line + '\n' + line, 4878)['guide_relaunch']), 2)

    def test_other_bundle_death_not_selected(self):
        line = '11-15 23:53:46.139  1059  3956 I C/tag: On ability died: /com.example.other/'
        self.assertEqual(events(line, 4878)['ams_guide_died'], [])


if __name__ == '__main__':
    unittest.main()
