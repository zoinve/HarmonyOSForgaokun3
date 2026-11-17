"""Analyze the failed user-observed517 run without changing acceptance labels."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'analyze-share-kernel-509.py').read_text()
    source=source.replace('commercial61-native-502','commercial61-native-517')
    source=source.replace('share-kernel-analysis-509.json','share-analysis-528.json')
    exec(compile(source,str(BASE/'analyze-share-517-528.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'analyze-share-517-528.generated.py')))
