"""Preserve failed 011; declare an existing ISO libc API missing from compiler headers."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
payload=runpy.run_path(str(base/'build-commercial-mesa-011.py'))['payload']
payload=payload.replace('commercial-mesa-011','commercial-mesa-012').replace('lab-commercial011','lab-commercial012')
anchor="headers=root/'sdk/native'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""symbols=subprocess.check_output(['readelf','-Ws',str(runtime/'libc.so')],text=True)
assert any(' FUNC ' in line and line.split()[-1]=='secure_getenv' for line in symbols.splitlines())
compat=work/'commercial-libc-api.h'
compat.write_text('#ifdef __cplusplus\\nextern "C" {\\n#endif\\nextern char *secure_getenv(const char *);\\n#ifdef __cplusplus\\n}\\n#endif\\n')
"""+anchor)
anchor="includes='-I'+str(root/'prefix/system/include')+' -fno-emulated-tls'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"+' -include '+str(compat)")
if __name__=='__main__':
    report=base.parent/'reports/commercial-mesa-012'
    assert not report.exists(),'preserve numbered builds'
    report.mkdir()
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=3100).returncode)
