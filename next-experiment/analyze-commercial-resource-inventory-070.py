from pathlib import Path

source=Path(__file__).with_name('analyze-commercial-resource-inventory-069.py').read_text().replace(
    'reports/commercial61-native-069','reports/commercial61-native-070')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
