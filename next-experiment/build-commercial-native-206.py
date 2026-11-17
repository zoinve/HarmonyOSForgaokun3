"""Build a new immutable revision; preserve uninstalled205 evidence."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'build-commercial-native-205.py').read_text().replace('205','206')
    exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
