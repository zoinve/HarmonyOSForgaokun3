"""Reuse immutable readers for the cmdline-corrected setup seed boot."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'analyze-commercial-114.py').read_text().replace(
        'commercial61-native-114','commercial61-native-124').replace(
        'commercial-workflow-114.py','commercial-workflow-124.py').replace("'114'","'124'")
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
