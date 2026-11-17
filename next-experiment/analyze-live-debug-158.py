"""Preserve the same runtime acceptance gate for the corrected root resolver."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'analyze-live-debug-157.py').read_text().replace('157','158')
    exec(compile(source,'analyze-live-debug-158.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'analyze-live-debug-158.generated.py')})
