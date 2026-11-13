# Experiment 958: genuine lock screen, desktop not yet verified

- Completed one bounded native ARM/KVM full-system run (363.758 seconds).
- All 13 downloaded PPM captures matched their recorded byte counts and SHA-256 hashes.
- Original SDK images, adapted read-only disks, and protected commercial userdata passed the runner's integrity checks.
- Independently viewed lossless PNG conversions of captures 2 and 13: genuine HarmonyOS lock screen, 1920x1080, account `user`, Chinese message requiring a password after reboot. The displayed clock advances from 07:59 to 08:04.
- This is not the standalone composer test pattern, but it is also not an unlocked desktop. Input and successful login remain unverified.
- PNG evidence: `reports/official-arm-958-visual/screen-2.png`, `screen-6.png`, and `screen-13.png`; original PPM evidence remains unchanged in `next-experiment/official-arm-run-958/`.
- Read-only evidence extraction completed: 10 hilog/fault files plus manifest preserved in `reports/official-arm-evidence-958-verified/`; all downloaded file sizes and SHA-256 hashes passed verification. The source userdata is retained unchanged.
- Keep completed experiment 958 immutable. Retain its writable userdata until evidence-preserving, exact guarded cleanup is appropriate. Do not bypass or alter account authentication to reach the desktop.
