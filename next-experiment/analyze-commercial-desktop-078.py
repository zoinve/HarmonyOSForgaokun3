from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'analyze-commercial-desktop-077.py'))['source']
source = source.replace("else '077'", "else '078'").replace(
    "['074', '075', '076', '077']", "['074', '075', '076', '077', '078']").replace('COMMERCIAL077', 'COMMERCIAL078')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
