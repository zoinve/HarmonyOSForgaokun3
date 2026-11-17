"""Declare ISO secure_getenv only after Mesa's own feature detection enables it."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
payload=runpy.run_path(str(base/'build-commercial-mesa-012.py'))['payload']
payload=payload.replace('commercial-mesa-012','commercial-mesa-013').replace('lab-commercial012','lab-commercial013')
start=payload.index('compat.write_text(')
end=payload.index("\nheaders=root/'sdk/native'",start)
call=payload[start:end]
assert call.endswith(')')
payload=payload[:start]+"compat.write_text('#ifdef HAVE_SECURE_GETENV\\n' + "+call[len('compat.write_text('):-1]+" + '\\n#endif\\n')"+payload[end:]
if __name__=='__main__':
    report=base.parent/'reports/commercial-mesa-013'
    assert not report.exists(),'preserve numbered builds'
    report.mkdir()
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=3100).returncode)
