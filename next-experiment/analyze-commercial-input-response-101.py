"""Retain original-keyboard and actual-timestamp correlation for 101."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
source = runpy.run_path(str(BASE/'analyze-commercial-input-response-099.py'))['source']
source = source.replace("else '099'", "else '101'").replace(
    "['075', '076', '077', '078', '099']", "['075', '076', '077', '078', '099', '101']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
