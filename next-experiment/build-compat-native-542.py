"""Prepare a separate real-cgroup probe candidate; do not install or boot it."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'build-share-native-502.py').read_text()
    source=source.replace('reports/share-supplicant-499/result.json','reports/share-supplicant-515/result.json')
    source=source.replace('commercial61-native-502','commercial61-native-542')
    assert source.count('        502, original')==1
    source=source.replace('        502, original','        542, original')
    assert source.count('update_config=0\n')==1
    source=source.replace('update_config=0\n','',1)
    source=source.replace('share-network-helper-501.py','compat-network-helper-526.py')
    old='(!strcmp(mode,"start") || !strcmp(mode,"share-start")) ? 15:5'
    assert source.count(old)==1
    source=source.replace(old,'!strcmp(mode,"compat-probe") ? 20 : '+old,1)
    anchor='    entries[\'native-target/share501\'] = (0o40700, b\'\')'
    assert source.count(anchor)==1
    source=source.replace(anchor,"    entries['native-target/compat525'] = (0o40700, b'')\n"+anchor,1)
    anchor='                if((i==4 || i==10) && started083)'
    assert source.count(anchor)==1
    source=source.replace(anchor,
        '                if(i==5 && started083)(void)network083_command(child,"compat-probe");\n'+anchor,1)
    exec(compile(source,str(BASE/'build-compat-native-542.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'build-compat-native-542.generated.py')))
