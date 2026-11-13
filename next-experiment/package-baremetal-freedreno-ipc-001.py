"""Fresh private probe and unchanged verified Mesa003/runtime dependencies; no execution/install."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
source=runpy.run_path(str(base/'baremetal-freedreno-ipc-probe-001.py'))['build_source']()
ipc_header=(base/'baremetal-buffer-ipc-001.h').read_text()
payload=runpy.run_path(str(base/'package-baremetal-freedreno-fence-002.py'))['payload']
payload='source='+repr(source)+'\nipc_header='+repr(ipc_header)+'\n'+payload[payload.index('\nheader=')+1:]
for old,new in [('baremetal-freedreno-fence-package-002','baremetal-freedreno-ipc-package-001'),
                ("work=root/'baremetal-freedreno-fence-002'","work=root/'baremetal-freedreno-ipc-001'")]:
    assert old in payload,old
    payload=payload.replace(old,new)
begin=payload.index("prior=root/'baremetal-freedreno-fence-001'")
end=payload.index("(report/'compile.stderr').write_text('')",begin)+len("(report/'compile.stderr').write_text('')")
payload=payload[:begin]+"""(work/'baremetal-buffer-ipc-001.h').write_text(ipc_header)
r=subprocess.run(args,capture_output=True,text=True,timeout=60)
(report/'compile.stdout').write_text(r.stdout);(report/'compile.stderr').write_text(r.stderr);r.check_returncode()"""+payload[end:]
anchor='probe_reused_unchanged=True,build_command_not_executed=args'
assert payload.count(anchor)==1
payload=payload.replace(anchor,"ipc_protocol_source_sha256=sha(work/'baremetal-buffer-ipc-001.h'),cross_process_gpu_execution_verified=False,build_command=args")
compile(payload,'ipc-probe001-package','exec')
if __name__=='__main__':
    out=base.parent/'reports/baremetal-freedreno-ipc-package-001'
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=120)
