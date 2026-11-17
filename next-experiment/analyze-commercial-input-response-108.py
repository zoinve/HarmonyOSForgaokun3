from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
source = runpy.run_path(str(BASE / 'analyze-commercial-input-response-107.py'))['source']
source = source.replace("else '107'", "else '108'").replace(
    "['075', '076', '077', '078', '099', '105', '107']", "['075', '076', '077', '078', '099', '105', '107', '108']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
