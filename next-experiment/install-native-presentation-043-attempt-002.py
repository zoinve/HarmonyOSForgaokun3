"""Fresh installation attempt: normalize the genuine list-shaped artifact manifest."""
from pathlib import Path
import re
import runpy


def artifact_table(rows):
    assert isinstance(rows, list) and len(rows) == 9
    result = {}
    for row in rows:
        assert set(row) == {'name', 'bytes', 'sha256'}
        name = row['name']
        assert isinstance(name, str) and Path(name).name == name and name not in ('.', '..')
        assert name not in result and isinstance(row['bytes'], int) and row['bytes'] >= 0
        assert re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
        result[name] = row
    return result


path = Path(__file__).with_name('install-native-presentation-043.py')
parent = runpy.run_path(str(path))
REMOTE = parent['REMOTE']
prepare_entry = parent['prepare_entry']
source = path.read_text(encoding='utf-8')
anchor = "candidate_artifacts=candidate['artifacts']"
assert source.count(anchor) == 1
source = source.replace(anchor, "candidate_artifacts=artifact_table(candidate['artifacts'])")
compile(source, 'install-native-presentation-043-attempt-002', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'install-native-presentation-043-attempt-002', 'exec'))
