from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'analyze-commercial-full-frame-085.py'))['source'].replace('commercial61-native-085', 'commercial61-native-086').replace('COMMERCIAL085_FULL_EXPORT', 'COMMERCIAL086_FULL_EXPORT')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
