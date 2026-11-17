"""Keep the proven native-channel acceptance checks for either persistence boot."""
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    assert sys.argv[1:] in [['166'],['167'],['168'],['169']]
    number=sys.argv[1]
    folder='commercial61-native-166-compile-fix-1' if number=='166' else 'commercial61-native-'+number
    source=(BASE/'analyze-live-debug-164.py').read_text()
    source=source.replace('commercial61-native-164',folder)
    source=source.replace('live-runtime-analysis-164.json','live-runtime-analysis-'+number+'.json')
    exec(compile(source,'analyze-live-debug-persistent-'+number+'.generated.py','exec'),
        {'__name__':'__main__','__file__':__file__})
