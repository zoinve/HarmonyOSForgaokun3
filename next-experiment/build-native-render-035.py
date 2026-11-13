"""Independent instrumented 034 composer; no optimization or cursor changes."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-native-render-034.py')))['payload']
payload=payload.replace("old=root/'native-cursor-032-r2';work=root/'native-render-034'", "old=root/'native-render-034';work=root/'native-render-035'")
payload=payload.replace("local=base.parent/'reports/native-render-034'", "local=base.parent/'reports/native-render-035'")
payload=payload.replace('native-cached-copy-034.h','native-cached-copy-035.h').replace('native-cached-copy-024.h','native-cached-copy-034.h')
payload=payload.replace('cached_landscape_copy_034(','cached_landscape_copy_035(').replace('cached_landscape_copy_024(','cached_landscape_copy_034(')
payload=payload.replace("r['commands'][1]","r['commands'][0]")
anchor="(work/'composer-trace.cpp').write_text(s)"
addition=r'''
anchor='bool cursor_painted032=paint_cursor_032(output);'
assert s.count(anchor)==1
s=s.replace(anchor,'auto paint_start035=perf_now_023();\n    '+anchor+'\n    perf_record_023("composer_ram_to_scanout035",paint_start035);',1)
'''
payload=payload.replace(anchor,addition+'\n'+anchor,1)
payload=payload.replace('AArch64 NEON exact-size rotation plus removal of intermediate frame copy; NOT GPU rotation','034 pixel path unchanged; split-stage diagnostic with bounded timing overhead; NOT GPU rotation')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)
