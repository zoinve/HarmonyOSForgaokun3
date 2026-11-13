# Candidate015: extracted composer-method native regression package

## Actual preparation result

The package was built once and independently parsed. Archive size: 31,333,026 bytes;
SHA-256 `2521acd99c47bf5465ea5ed2fe0eb0d687491350d4956058f8de5d4309abae53`.

Compared with completed native candidate014, only
`opt/native-mesa-001/probe` changed and one record was added:
`opt/native-mesa-001/lib/libcomposer-methods-001.so`.
All other existing records retain identical contents, modes, UID and GID.
The independent audit also verified all 620 inert-parent records, all ten
private runtime files, kernel/DTB/helper/launcher hashes and matching local/WSL
manifests. See `baremetal-diagnostic-init-015/independent-verification.json`.

The kernel remains
`4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`.
Diagnostic init, identity helper, modules, eight original runtime libraries and
the render-only namespace launcher are unchanged. Completed trials, their raw
logs and cleanup009 were not rerun.

## Scope

This exact test bundle already passed on the MateBook under Ubuntu, with
independent file, effective sandbox-policy and system-preservation verification
in `baremetal-composer-probe-run-003/independent-verification.json`.
The separate consumer calls the reference's extracted client-buffer admission,
fence-wait, retained-FD and clear methods. It closes caller descriptors, imports
from the retained descriptor, clears that retained descriptor and then checks
real GPU pixels through the independently retained GBM buffer reference.

This is a private reduced-State method test, **not** the full target std::__h
container ABI, HDI wire protocol, RenderService integration or a usable composer.
It calls neither InitDisplay nor Commit and introduces no KMS or display-mode
change, primary DRM access, identity assignment or permission exception.
Native diagnostic SELinux initial enforcing without a loaded policy is not
policy-authorized graphics evidence. Initially unsignaled fences and a native
HarmonyOS desktop remain unverified.

## Current status

Candidate015 is prepared and independently archive-verified only. It has not
been staged on the MateBook, installed on EFI or booted. No new native-method
runtime success is claimed. No jobs remain running.

Before a future native run, use fresh numbered staging/boot/collection records,
verify all 340 saved trial011 logs, preserve Ubuntu default and logical
screen-off, retain the 64MiB EFI reserve and immediately attempt bounded SSH
reconnection following any authorized one-shot reboot. Never rerun consumed
trial011 or cleanup009 operational scripts.
