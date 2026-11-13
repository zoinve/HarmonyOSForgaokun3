# Original service graph observation 066

## Actual progress

- The unchanged original RenderService ran as UID1003 in its original domain.
  Its real software-Mesa EGL contexts were created and `eglMakeCurrent` returned1.
  Original composer/allocator identities and domains were also verified.
- The original HiLog query completed normally and returned actual decoded
  RenderService messages, including a client's `SET_SCREEN_CHANGE_CALLBACK` and
  `SetExposedEventCallback`. This is not screen composition or desktop proof.
- The same messages show unavailable MemMgrService / SA1909 and resource
  scheduling service connections. The observation does not yet establish whether
  these are startup delays or persistent dependency failures.
- The original screen query returned exit3 with no useful screen dump. Its cause
  is unknown; no permissions or tokens were fabricated to make it pass.

## Dictionary evidence

Read-only inspection of the genuine decoder confirms lookup by reversed UUID
bytes and a filename prefix in `/data/log/dict`, not the guessed cache-JSON mount
used in failed trial065. During trial066, the real RenderService dictionary was
absent at samples9/13 and present/readable at sample17, with261919 bytes and the
original `init physical: {` prefix. This establishes late availability, not a
general explanation for every undecoded message.

## Verification and boundaries

- `reports/original-graphics-boot-066-independent.json` independently checks18
  permissive-mode samples, original identities/domains, actual EGL results,
  twelve injected files, kernel/initrd, all three original SDK images and378
  prior native raw logs.
- The 160-second disk-isolated TCG guest observation timed out; neither a
  Foundation critical fault nor guest reboot was observed within that interval.
  A bounded observation is not a successful or clean service shutdown.
- Serial SHA256:
  `a98035207e55d75896414e15f377f6167fa8abf7628a03a97826aa489a3ddcd1`.
- No MateBook/Ubuntu changes or physical scanout were performed. Original images
  remained read-only; only disposable guest RAM overlays/data were changed.
- Complete HDF/display readiness, frame delivery, SceneBoard and an interactive
  HarmonyOS desktop remain unverified.

## Next observation

Fresh trial067 retains the exact graphics providers, kernel and original service
configuration. It extends passive sampling and adds late original-tool queries
under a360-second guest bound. Completed trial066 is not rerun or overwritten.
