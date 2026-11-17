"""Recheck the probe after making the child gate immune to SIGPIPE."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'test-compat-cgroup-527.py').read_text().replace('527','547')
    exec(compile(source,str(BASE/'test-compat-cgroup-547.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'test-compat-cgroup-547.generated.py')))
