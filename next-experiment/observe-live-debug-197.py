'''Read-only authenticated Settings observation for the isolated197 candidate.'''
from pathlib import Path

BASE=Path(__file__).resolve().parent

if __name__=='__main__':
    source=(BASE/'observe-live-debug-159.py').read_text()
    source=source.replace('reports/commercial61-native-159','reports/commercial61-native-197-r1')
    source=source.replace('harmony-native-159','harmony-native-197')
    anchor="            if discovered.returncode or len(payload['endpoints']) != 1:"
    assert source.count(anchor)==1
    source=source.replace(anchor,"            print(json.dumps(dict(utc=stamp(),discovered_addresses=[row['address'] for row in payload['endpoints']],authenticated=False)),flush=True)\n"+anchor,1)
    exec(compile(source,'observe-live-debug-197.generated.py','exec'),
         {'__name__':'__main__','__file__':str(BASE/'observe-live-debug-197.generated.py')})
