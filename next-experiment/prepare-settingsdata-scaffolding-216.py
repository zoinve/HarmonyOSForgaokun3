"""Preserve failed 215; add source-derived missing ancestors in new local 216."""
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
API = runpy.run_path(str(HERE / 'prepare-settingsdata-scaffolding-215.py'))

if __name__ == '__main__':
    assert sys.argv[1:] in [['plan'], ['prepare']]
    if sys.argv[1] == 'plan':
        old = API['WORK'] / 'data.ext4'
        report = API['REPORT']
        assert old.is_file() and not (report / 'result.json').exists()
        assert not subprocess.check_output(['losetup', '-j', str(old)]).strip()
        failure = dict(stage='mkdir provider base; missing parent in pristine source',
            exit_status=1, provider_directory_created=False, candidate_unmounted=True,
            failed_candidate_preserved=True, target_modified=False,
            revision='216 adds original ancestor directory metadata; no invented owner/mode')
        (report / 'failure.json').open('x').write(json.dumps(failure, indent=2))
    for key in ['WORK', 'REPORT']:
        value = API[key].with_name(API[key].name.replace('215', '216'))
        API['plan'].__globals__[key] = value
        API['prepare'].__globals__[key] = value
    (API['plan'] if sys.argv[1] == 'plan' else API['prepare'])()
