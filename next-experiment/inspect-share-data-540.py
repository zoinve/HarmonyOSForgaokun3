"""Read selected cumulative P2P counters after532, retaining privacy limits."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'inspect-share-data-530.py').read_text()
    source=source.replace('commercial61-native-517','commercial61-native-532')
    source=source.replace('boot-observation-522.json','boot-observation-536.json')
    source=source.replace('share-data-analysis-530.json','share-data-analysis-540.json')
    source=source.replace('harmony-share-lab-530','harmony-share-lab-540')
    source=source.replace('harmony-share-data-530','harmony-share-data-540')
    source=source.replace('inspect-share-data-530.generated','inspect-share-data-540.generated')
    exec(compile(source,str(BASE/'inspect-share-data-540.wrapper.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'inspect-share-data-540.wrapper.py')))
