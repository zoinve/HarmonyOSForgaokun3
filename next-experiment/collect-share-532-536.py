"""Collect532 once, excluding canonical runs through517."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'collect-cpufreq-471-475.py').read_text()
    source=source.replace('commercial61-native-471','commercial61-native-532')
    source=source.replace('commercial-return-audit-471','commercial-return-audit-532')
    source=source.replace("'458']","'458', '471', '502', '517']")
    source=source.replace(".replace('279', '475')",".replace('279', '536')")
    exec(compile(source,str(BASE/'collect-share-532-536.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'collect-share-532-536.generated.py')))
