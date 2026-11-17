# Candidate 172 withheld before installation

The lifecycle-only candidate compiled successfully, retaining runtime 168 bytes
and incorporating the tested explicit target-namespace data-mount teardown.
It was not installed, selected or booted. Build artifacts and result/overlay
metadata remain immutable under `commercial61-native-172`.

Before installation, inspection of completed boot 168 established a concrete
warm-start failure: phase-172.log reports at line 279773 that
`commercial-collaboration-ready116.sh` cannot create its existing diagnostic log,
followed by `COMMERCIAL116_HOME_GATE_FAILED status=1`. The copied collaboration
log belongs to the earlier persistent boot, not the current boot. Consequently
it cannot establish a current readiness checkpoint.

Candidate 173 adds archival of the omitted adaptation-owned diagnostic logs and
FIFOs before original init starts, preserving the original checkpoint script,
launch commands and security checks byte-for-byte. It also retains the 172
lifecycle fix. This supersedes 172 for the next new boot; it is not another
OOBE/activation experiment. No old boot is rerun, no application database or seed
is reset, and no original image is modified.
