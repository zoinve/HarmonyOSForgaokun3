"""Fresh build with Clang compatibility for Mesa's generated C++ register initializers."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent.parent
out = base / 'reports/baremetal-mesa-freedreno-build-002'


def build_payload():
    parent = Path(__file__).with_name('build-baremetal-mesa-freedreno-001.py')
    source = runpy.run_path(str(parent), run_name='offline_adapter')['payload']
    for old, new in [('baremetal-mesa-freedreno-001', 'baremetal-mesa-freedreno-002'),
                     ('baremetal-mesa-freedreno-build-001', 'baremetal-mesa-freedreno-build-002'),
                     ('lab-freedreno001', 'lab-freedreno002')]:
        assert old in source
        source = source.replace(old, new)
    anchor = "root=Path('/home/zoinve/harmony-virgl-883')"
    source = source.replace(anchor, "os.environ['PYTHONDONTWRITEBYTECODE']='1'\n" + anchor)
    anchor = "'-Dvideo-codecs=','-Dc_args='+includes,'-Dcpp_args='+includes]"
    assert source.count(anchor) == 1
    source = source.replace(anchor, "'-Dvideo-codecs=','-Dc_args='+includes,'-Dcpp_args='+includes+' -Wno-c++11-narrowing']")
    compile(source, 'freedreno-build-002', 'exec')
    return source


if __name__ == '__main__':
    payload = build_payload()
    assert not out.exists(), 'Preserve numbered build reports'
    out.mkdir()
    subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
                   text=True, check=True, timeout=3100)
