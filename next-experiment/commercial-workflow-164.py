"""Use the admitted small-loader workflow with a distinct immutable run."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
source=(BASE/'commercial-workflow-161.py').read_text()
for old,new in [('source161','source164'),('commercial61-native-161','commercial61-native-164'),
    ('commercial-return-audit-161','commercial-return-audit-164'),('live-debug-helper-161','live-debug-helper-164'),
    ('live-debug161','live-debug164'),("['live161']","['live164']"),
    ('ordered_chain_equals_full_161','ordered_chain_equals_full_164'),('estimated161','estimated164'),
    ('native staged storage diagnostic 161','native current-namespace log diagnostic 164')]:
    source=source.replace(old,new)
anchor='    return source'
assert source.count(anchor)==1
source=source.replace(anchor,'''    if operation == 'retrieve-commercial-evidence':
        newest = json.loads((ROOT / 'reports/commercial61-native-161/runtime-evidence/retrieval-manifest.json').read_text())['run']
        source = source.replace('if p.name not in [','if p.name not in [' + repr(newest) + ', ',1)
''' + anchor,1)
namespace={'__name__':__name__,'__file__':str(BASE/'commercial-workflow-164.generated.py')}
exec(compile(source,'commercial-workflow-164.generated.py','exec'),namespace)
globals().update({name:value for name,value in namespace.items() if not name.startswith('__')})
