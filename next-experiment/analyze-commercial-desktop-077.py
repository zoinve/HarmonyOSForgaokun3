from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'analyze-commercial-desktop-076.py'))['source']
source = source.replace("else '076'", "else '077'").replace(
    "['074', '075', '076']", "['074', '075', '076', '077']").replace('COMMERCIAL076', 'COMMERCIAL077')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
