"""Preserve 070 real resources and observe original decoder failures."""
from pathlib import Path
import runpy

b=Path(__file__).resolve().parent
p=runpy.run_path(str(b/'build-commercial-native-070.py'))
h=runpy.run_path(str(b/'commercial-codec-observer-071.py'))
inner=h['inner'](p['inner'])
outer=h['outer'](p['outer']).replace('commercial61-native-070','commercial61-native-071').replace('COMMERCIAL070','COMMERCIAL071')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace(
    'outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-070','commercial61-native-071')
if __name__=='__main__':
    exec(compile(payload,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
