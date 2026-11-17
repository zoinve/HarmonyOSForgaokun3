"""Retire only the unreferenced502 ESP overlay; retain its existing backup."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'cleanup-retired-overlays-520.py').read_text()
    source=source.replace('commercial61-native-502.conf','commercial61-native-517.conf')
    source=source.replace("['set458.img','set471.img']","['set502.img']")
    source=source.replace("['458','471']","['502']")
    source=source.replace('retired-overlays-520','retired-overlay-534')
    exec(compile(source,str(BASE/'cleanup-retired-overlay-534.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'cleanup-retired-overlay-534.generated.py')))
