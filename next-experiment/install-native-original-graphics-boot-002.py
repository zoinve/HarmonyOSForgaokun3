"""Install counted 002, retaining 001 and every prior log; never select/reboot."""
from pathlib import Path

source=Path(__file__).with_name('install-native-original-graphics-boot-001.py').read_text()
source=source.replace('native-original-graphics-boot-001','native-original-graphics-boot-002')
source=source.replace('native-original-graphics-001','native-original-graphics-002')
source=source.replace("['009','010']","['011','013']")
source=source.replace('native trial 001','native trial 002')
if __name__ == '__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
