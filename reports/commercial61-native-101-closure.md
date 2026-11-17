# Native desktop experiment 101 closure

## Scope and result

The supplied image remains the baseline shared with HarmonyMac. No image-version
explanation is established. The only service configuration delta from 099 was
removing the original SoftBus BLE LD_PRELOAD entry, as the reference adaptation
does. Authentication, OOBE recovery and original application watchdogs remained.

Result: no stable interactive native desktop was demonstrated. This experiment
is complete and must not be repeated or its evidence overwritten.

## Execution and preservation

- Run: commercial61-native-087-7d1325af-0503-4cb3-9d32-3a81a3d6b758.
- Started 2026-11-15 10:49:41 UTC; Ubuntu return observed 10:53:25 UTC.
- All 132 retrieved files matched remote hashes; retrieval was read-only and
  unmounted afterwards. The bounded target run ended at phase 120.
- Original images and firmware were unchanged. Ubuntu remained the default;
  the screen-off timer was enabled and active.
- Entry 095 was archived before authorized removal; experimental entries
  099 and 101 were retained. Other EFI differences were limited to the normal
  random seed. See post-return-verification.json for detailed checks.

## Runtime findings

The reference force-stop succeeded: guide PID 6684 exited at 18:51:25.214.
SceneBoard PID 4575 received its native session exception at 25.241 and executed
the JS recovery callback at 32.652, relaunching the guide. Foundation then killed
SceneBoard for THREAD_BLOCK_6S at 33.077. Replacement SceneBoard PID 9578 and guide
PID 9976 persisted in later window samples, with the guide focused.

The complete original appfreeze snapshot has SHA256
6dd27693aa7b76b241e32f0194052fb1954497847f51642b2c36b83dd56e132c.
Its main-thread stacks show condition_variable/future waiting through the
DeviceDetect client, DevicePicker client and Js_GetTrustedDeviceListSync.
Related thread stacks show Binder SendRequest/WaitForCompletion through the
DeviceDetect client. These locate a real synchronous wait, but do not identify
the remote service or prove its root cause. See freeze-stack-analysis.json and
freeze-worker-analysis.json. The first query took 13039 ms; the replacement
process's 20 ms query is not a controlled latency comparison.

## Evidence limits

Only the 145-second SoftBus observer sample survived: expected config present,
PID 1188, readable mappings, removed preload absent. The observer appended to
a log whose main writer used a non-append file position, overwriting earlier
samples. Continuous process/config verification is therefore not established.
Future observers need an independently exported log; do not modify or rerun 101.

Two full 2560x1600 source frames were recovered with verified rotation. They
differ by 9276 pixels; both OCR results were empty and the image viewer rejected
the inputs. No visual desktop claim is possible. The physical Meta key pair
reached replacement SceneBoard, but a correlated visible response is unproven.
The reference script's unconditional READY output is not desktop acceptance.

## Next boundary

Map the original DeviceDetect Binder request to its server and compare actual
service dependencies against the pinned reference adaptations. Do not infer
commercial activation is required for the development desktop. Do not replace
the supplied image, forge provisioning state, disable recovery, or introduce
another boot until a meaningful changed-condition hypothesis is supported.
