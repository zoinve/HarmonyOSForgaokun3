"""New evidence filename; preserve the original conservative 077 analysis."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'analyze-commercial-input-response-078.py'))['source']
source = source.replace("else '078'", "else '077'").replace(
    "'input-response-analysis.json'", "'input-response-analysis-revision2.json'")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
