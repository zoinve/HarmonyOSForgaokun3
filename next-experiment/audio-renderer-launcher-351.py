"""Reuse the verified namespace entry path, not the rejected aa caller."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
def launcher351():
 source=(BASE/'native-bluetooth-ui-339.h').read_text()
 old='''char *const args[]={"/system/bin/aa","start","-b","com.huawei.hmos.settings",
            "-a","com.huawei.hmos.settings.BluetoothSettingsAbility","-m","pc_settings",NULL};'''
 assert source.count(old)==1
 source=source.replace(old,'char *const args[]={"/audio350/renderer",NULL};')
 source=source.replace('NATIVE_BLUETOOTH_UI_339_H','NATIVE_AUDIO_LAUNCHER_351_H')
 source=source.replace('bluetooth339-start.log','audio351-renderer.log')
 source=source.replace('bt339','audio351').replace('BT339','AUDIO351')
 source=source.replace('original_aa=1 original_ability_permission_checks=1 discovery_not_inferred=1',
   'original_ohaudio_api=1 original_permission_checks=1 playback_not_inferred=1')
 source=source.replace('AUDIO351_AA_EXIT','AUDIO351_HELPER_EXIT')
 source=source.replace('window_and_discovery_not_inferred','audible_output_not_inferred')
 return source.replace('8000','20000')
