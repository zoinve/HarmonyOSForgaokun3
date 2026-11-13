# Native diagnostic trial 001: collected evidence

Evidence: `baremetal-native-trial-001-evidence-immediate/collection.json` and its 20 SHA-256/size-verified phase logs. The delayed collector was intentionally cancelled after the user requested immediate collection; its exit code 1 is not a diagnostic boot failure.

## Confirmed

- Diagnostic kernel `7.1.0-rc3-gaokun3-el2` executed on Matebook E Go, with `harmony.diag=1` and the intended diagnostic initramfs.
- All eight CPUs started. PCIe Gen3 x4 and NVMe discovery succeeded; partitions p1–p4 were enumerated.
- The identity-guarded lab partition mounted successfully. Twenty persistent phase logs were retrieved and independently size/SHA-256 checked locally.
- Final log contains `NATIVE_DIAGNOSTIC_END desktop_verified=0`.
- Collection ran in the default Ubuntu kernel `7.1.0-rc3-gaokun3+`, with a changed boot ID. Diagnostic entry is now `harmony-native-diag-004+0-1.conf` (attempt consumed).
- Of the 58 pre-existing EFI files compared, only `loader/random-seed` changed. This is boot-generated state, not evidence of a changed Ubuntu loader configuration.

## Not working / not established

- Enumeration returned status 1: `/dev/dri` did not exist and no DRM connector was listed.
- Input enumeration showed only `gpio-keys` and the EC LID device; the touchscreen was not present at that observation.
- All requested modprobe phases returned 0, but this establishes module insertion/dependency handling, not completed driver binding or physical display/input operation.
- Captured kernel messages end near 1.05 seconds. Deferred probing or asynchronous initialization remains a hypothesis requiring evidence, not a diagnosed root cause.
- Final END marker precedes the final unmount/reboot path; return to Ubuntu does not independently prove successful unmount or which reboot path executed.
- HarmonyOS was not launched. No native HarmonyOS compatibility, desktop, display scanout, or touch functionality is established.

## State / next work

The collector mounted only the lab partition read-only with `noload,nodev,nosuid,noexec`; leave it read-only while preserving evidence. No further boot is scheduled or authorized by this report. Next offline work should inspect display/input supplier dependencies and add bounded driver-binding/deferred-probe observations before proposing another numbered trial. Do not rearm or rerun trial 001.
