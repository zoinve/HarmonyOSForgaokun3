"""Add a private, bounded real-controller probe after target identity checks."""
from pathlib import Path
import runpy

BASE=Path(__file__).resolve().parent
SOURCE=runpy.run_path(str(BASE/'share-network-helper-501.py'))['SOURCE']
anchor='"share-start", "share-observe"'
assert SOURCE.count(anchor)==1
SOURCE=SOURCE.replace(anchor,anchor+', "compat-probe"',1)
anchor='static int run_mode(const char *mode)\n{'
assert SOURCE.count(anchor)==1
SOURCE=SOURCE.replace(anchor,(BASE/'native-compat-cgroup-525.c').read_text()+'\n'+anchor+
    '\n    if(!strcmp(mode,"compat-probe")) return compat525_probe();',1)
