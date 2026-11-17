"""New diagnostic follows restored display policy; historical scripts stay intact."""
from pathlib import Path
import ast,runpy
base=Path(__file__).resolve().parent
for stem in ['install-commercial-native','run-commercial-native','verify-commercial-return']:
    path=base/(stem+'-023.py')
    assert path.exists(),'missing enabled-screen-off workflow: '+stem
    source=runpy.run_path(str(path))['source'];ast.parse(source)
    assert 'HostName=192.168.10.128' in source and 'HostKeyAlias=192.168.10.128' in source
    assert 'commercial61-native-023' in source
    assert "=='disabled'" not in source and "=='inactive'" not in source
    assert "=='enabled'" in source and "=='active'" in source
    assert 'timer_disabled=True' not in source
print('PASS: new workflows enforce enabled/active screen-off and trusted 192 connection')
