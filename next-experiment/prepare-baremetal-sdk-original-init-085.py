"""AArch64 uses 64-bit file offsets; retain notification-only observation."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-084.py')))
source = parent['source'].replace('ORIGINAL_INIT084_', 'ORIGINAL_INIT085_').replace('GRAPHICS084_', 'GRAPHICS085_')
source = source.replace('graphics_profile_events_084', 'graphics_profile_events_085')
assert source.count('O_RDONLY | O_LARGEFILE | O_CLOEXEC') == 1
source = source.replace('O_RDONLY | O_LARGEFILE | O_CLOEXEC', 'O_RDONLY | O_CLOEXEC')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-084', 'baremetal-sdk-original-init-085')
compile(payload, 'original-profile-events-085-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'], input=payload,
                                   text=True, timeout=180).returncode)
