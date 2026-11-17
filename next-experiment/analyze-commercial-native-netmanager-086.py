from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'analyze-commercial-native-netmanager-085.py'))['source'].replace('commercial61-native-085', 'commercial61-native-086')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
