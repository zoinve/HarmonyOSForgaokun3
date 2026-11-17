"""Retain full-frame OCR/differences and native identity checks for 104."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
source = runpy.run_path(str(BASE/'review-commercial-return-101.py'))['source']
source = source.replace('commercial61-native-101', 'commercial61-native-104')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
