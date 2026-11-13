"""Retain every existing EFI file; install audited two-member acceleration overlay."""
from pathlib import Path
import subprocess,json
base=Path(__file__).resolve().parent
source=(base/'install-native-return-overlay-033.py').read_text()
source=source.replace('native-original-graphics-boot-033','native-original-graphics-boot-034').replace('native-original-graphics-033','native-original-graphics-034')
source=source.replace('HarmonyOS 033 - Cursor test - AUTO RETURN 7 MIN','HarmonyOS 034 - NEON render - AUTO RETURN 7 MIN')
meta=json.loads((base.parent/'reports/native-original-graphics-boot-034/return-overlay-result.json').read_text())
assert meta['only_changed_member']==['init','native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so']
source=source.replace('e90f60b8171e9a1e2ce6128d473b822a2c7a60d7dcbc831bd5ab6b291b3f6f65',meta['overlay_sha256'])
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
