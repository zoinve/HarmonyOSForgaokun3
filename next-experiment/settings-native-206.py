"""Reserve retry75 exclusively for an unready gate, never an aa launch result."""
from pathlib import Path
import runpy

BASE=Path(__file__).resolve().parent
PREVIOUS=runpy.run_path(str(BASE/'settings-native-205.py'))
EXPECTED_DATA=PREVIOUS['EXPECTED_DATA']


def outer206(source):
    return PREVIOUS['outer205'](source).replace('/commercial61-native-205/',
        '/commercial61-native-206/').replace('settings-launch-205.h',
        'settings-launch-206.h').replace('settings205_start','settings206_start')


def header206():
    source=PREVIOUS['header205']().replace('settings205','settings206').replace('SETTINGS205','SETTINGS206')
    old='exec /system/bin/aa start -b com.huawei.hmos.settings -a com.huawei.hmos.settings.MainAbility -m pc_settings'
    new='/system/bin/aa start -b com.huawei.hmos.settings -a com.huawei.hmos.settings.MainAbility -m pc_settings; result=$?; [ $result -ne 75 ] || exit 76; exit $result'
    assert source.count(old)==1
    return source.replace(old,new,1).replace('SETTINGS_LAUNCH_201_H','SETTINGS_LAUNCH_206_H')
