# Original graph 076: successful Commit, no desktop image

## Verified outcome

- The real reference composer in original `composer_host` PID1180 / UID3036
  returned **0** from `Commit`. This is one distinct captured result record,
  not a count of frames or proof of sustained presentation.
- The genuine hotplug callback returned. Original services retained their
  credentials, and the guest retained loaded SELinux policy in permissive mode.
- Independent QMP scanout capture remained nearly black at120s (16 nonblack
  pixels) and completely black at240s and330s. All captures were1280x800.
  These are virtual-display observations, not a HarmonyOS desktop or physical
  MateBook display test.
- Bounded process snapshots at samples17 and29 contained Foundation and
  appspawn, but no SceneBoard process. This does not establish that the bundle
  is absent or that it never ran outside those snapshots.
- No Foundation critical fault or guest reboot was observed within360s.

## Evidence and preservation

- `reports/original-graphics-boot-076-independent.json`
- `reports/baremetal-sdk-original-init-qemu-076/`
- `next-experiment/original-composer-trace-003.py` records actual return values
  without changing their evaluation, values, original calls or callbacks.
- Independent checks covered all12 injected provider files, the genuine ashmem
  module, archive, matching virtual kernel, three complete original SDK images,
  and all378 prior native raw files. PNG and PPM pixels were compared directly.
- No Ubuntu/MateBook connection, host module load or boot change was performed.
  This is not a fresh physical screen-off check.

## Next bounded integration step

Experiment077 uses the genuine original `bm dump` bundle query and the normal
original `aa start` request matching the installed SceneBoard HAP metadata and
HarmonyMac reference. It preserves real responses and authorization failures;
it neither changes identities nor bypasses authentication, activation or the
startup guide. Later virtual scanout captures will determine what is actually
displayed. At this report's creation077 is running; its outcome is not claimed.
