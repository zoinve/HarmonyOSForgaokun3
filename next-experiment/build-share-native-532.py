"""Remove the unsupported write-control field from the no-config-write P2P build."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'build-share-native-502.py').read_text()
    assert source.count('reports/share-supplicant-499/result.json')==1
    source=source.replace('reports/share-supplicant-499/result.json','reports/share-supplicant-515/result.json')
    source=source.replace('commercial61-native-502','commercial61-native-532')
    assert source.count('        502, original')==1
    source=source.replace('        502, original','        532, original')
    assert source.count('update_config=0\n')==1
    source=source.replace('update_config=0\n','',1)
    exec(compile(source,str(BASE/'build-share-native-532.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'build-share-native-532.generated.py')))
