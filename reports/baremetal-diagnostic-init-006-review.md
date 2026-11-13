# Observation-only diagnostic 006

Purpose: separate early sampling from a missing DRM supplier/component chain. Trial002/005 registered the Himax input device but sampled DRM at about 1.18 seconds; working Ubuntu finishes DRM binding later. Missing explicit Gaokun UCSI remains a separate hypothesis, not a proven sole cause.

006 deliberately retains the exact 005 module plan. After that plan it observes `/dev/dri/card0` as a character device together with `/sys/class/drm/card0`, up to 20 quarter-second sleeps. It exits immediately on the condition; a missing node exits 124. A normal file does not count. Neither observation result proves display output or HarmonyOS compatibility. The surrounding phase has an 8-second process timeout, is admitted through the unchanged shared 180-second budget with 30-second reserve, and does not alter the fallback reboot or security gates.

Read-only binding snapshots additionally cover both DP controllers, GPU/GMU, auxiliary devices and UCSI children. The final snapshot and existing input/DRM enumeration follow the observation window even if its condition was not met, subject to the original budget gates.

Verification before packaging:

- `baremetal-observation-006-command-audit.json`: exact generated BusyBox commands executed on ARM64. A regular file timed out without success after 5.108 seconds; an existing character-node fixture returned in 0.0013 seconds; a delayed fixture returned in 0.507 seconds. These are filesystem-condition tests using `/dev/null`, not simulated GPU/DRM functionality. The extended binding command also completed on Ubuntu.
- `baremetal-diagnostic-006-tests.txt`: 26 targeted checks passed, including 006 real C snapshot harness, unchanged core and budget tests, observation source contracts, screen-off policy and reconnect tests. This is not a unified repository test suite or hardware success claim.
- `baremetal-lab-workspace-rw-003.json`: all 50 collected trial001+002 log files independently size/hash checked locally and on the device before and after restoring only the lab preparation mount flags. Existing evidence was not changed.
- Generated C SHA-256: `194f74cfc34e07609ee7a3d21c6bb7149240b7640661a1b688803ef7ce5b3c92`.

Packaging completed separately: `baremetal-diagnostic-init-006.json` records a 24,217,417-byte archive, SHA-256 `842e29b1c4a78fbbed4d2784f7833e7fffaca483eeedcc2cdc649fe576d4276e`, with all base entries unchanged, verified archive round-trip and actual ARM64 non-PID1 refusal. Prior archives were not regenerated.

A native trial is a separate step. No display, touch-event, native HarmonyOS or hard-lock recovery success is established by the above checks. Ubuntu startup screen-off applies after Ubuntu returns, not to firmware or the independent diagnostic initramfs.
