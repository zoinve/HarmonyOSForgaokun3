from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'cleanup-unused-esp-overlays-309.py').read_text()
    source=source.replace('unused-esp-overlays-cleanup-309.json','unused-esp-overlays-cleanup-406.json')
    source=source.replace('commercial61-native-297.conf','commercial61-native-394.conf')
    source=source.replace('[197,201,206,235,253,262,266,276,285,294]','[385]')
    exec(compile(source,'cleanup-unused-esp-overlays-406.generated.py','exec'),
        dict(__name__='__main__',__file__=str(BASE/'cleanup-unused-esp-overlays-406.generated.py')))
