"""Observe the new root-resolution candidate without repeating boot 157."""
from pathlib import Path

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'observe-live-debug-157.py').read_text().replace('157','158')
    source = source.replace('reports/live-debug-inputs-158','reports/live-debug-inputs-157')
    exec(compile(source,'observe-live-debug-158.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE / 'observe-live-debug-158.generated.py')})
