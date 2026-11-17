"""Correlate unchanged physical keyboard input with actual 104 timestamps."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
source = runpy.run_path(str(BASE/'analyze-commercial-input-response-099.py'))['source']
source = source.replace("else '099'", "else '104'").replace(
    "['075', '076', '077', '078', '099']", "['075', '076', '077', '078', '099', '104']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
