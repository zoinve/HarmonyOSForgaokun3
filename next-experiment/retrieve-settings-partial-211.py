"""Recover206 evidence with unchanged privacy scans and a verified prior digest."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'retrieve-early-driver-131.py').read_text()
    source=source.replace('commercial61-native-131','commercial61-native-206')
    source=source.replace('commercial61-native-130','commercial61-native-201')
    source=source.replace('commercial-workflow-131.py','commercial-workflow-206.py')
    source=source.replace('retrieve-early-driver-131','retrieve-settings-partial-211')
    exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
