# Native 044 — original SceneBoard and bounded KMS evidence

## Return and preservation

The single authorized 044 boot returned to Ubuntu after **308.307 s**, using immediate-first bounded SSH probing (77 observations). Independent verification succeeded once: `native-original-graphics-boot-044/post-return-verification.json`.

- Returned boot ID: `98f25442-d15e-47b4-9a83-388002293439`; kernel `7.1.0-rc3-gaokun3+`.
- Ubuntu default, firmware and automatic screen-off remain intact; no pending one-shot and the lab partition is unmounted. Logical greeter state was already off; the verifier did not set it. Physical screen state was not observed.
- All 71 new raw files, 71 prior 043 files, 71 prior 041 files, 378 older diagnostic files and three full original SDK images passed hash checks. Existing EFI content stayed unchanged except fresh `loader/random-seed`; it was **not restored**. The own counted 044 entry was consumed with unchanged bytes.
- Actual native kernel/044 overlay, genuine `/mnt` tmpfs verification and 12 permissive SELinux observations were checked. Original policy, services, credentials, login, sandbox and watchdog protections were not replaced or bypassed.

## Actual application and image evidence

Original AppSpawn reports `com.ohos.sceneboard` PID 2265, **result 0**, at 08:00:30.732. Its original application logs continue, followed by its engine-service process. This is not merely a mapped library or a fabricated ready flag.

The already verified `phase-069.log` contains two complete captured scanout-file reads (samples 9 and 11). The existing strict, pure `extract-native-scanout-013.py` functions were reused without executing that old experiment's main. Both reconstruct identical **160×256 RGB downsampled images**, losslessly exported under `native-presentation-044-scanout/`. Visual inspection shows the genuine rotated lock/login screen, avatar and password prompt. These are reads of a captured scanout file, **not two proven distinct presented frames**, not an unlocked desktop, and not a human observation of the panel.

Source SHA-256: `08babc5a3b914a5b913cdc1afcf3f23582127daaf45733868dfbb28b96dad3eb`; PPM SHA-256: `b2b3ef5aea4bef428279e915822a4ed611bff5c70c62178586a34f2e23559dcf`. Exact extraction provenance is in the new scanout `result.json`. Old raw evidence was not rewritten.

## Why this is not an FPS result

The frozen 043 analyzer matched **22 client completion callbacks, zero cursor callbacks**, but rejected the aggregate timing window. Sixteen kernel event timestamps are **2–34 µs later** than their local callback timestamps; other offsets reach −1294 µs. The mechanism has not been established. The strict old result is retained, not relaxed with an arbitrary tolerance. There is no stable-120-FPS, unique-changing-content, sustained-workload, thermal or physical-input acceptance claim.

A separate, concrete capture defect was identified: `diagnostic_file_002` reads only **32767 bytes from the beginning** of the shared performance file. In the final raw phase, samples 6–11 all hit that exact bound; the journal ends with a partial submission 23. Thus the 22 matched callbacks cover only local times **31.852578–34.403863 s**, not the entire native session. The 111 rejected cumulative lines must not be interpreted as 111 rendering failures. Old journals, analysis and successful verifier remain immutable.

## Fresh 045 candidate, not yet deployed at this writing

045 changes only the diagnostic observer to read new complete trace lines incrementally. It preserves partial final lines for later samples, validates regular no-follow file access, bounds each sample to 1 MiB and the run to 2 MiB, reports errors/resets/limits explicitly, and does not alter writer batching, rendering, input, timestamps or original services. Writer-buffer tails and capture limits remain unknown coverage, not success.

Four explicit offline tests passed, including real host-file reads beyond the old prefix, partial-line continuation, read failures, capacity-counter honesty and source reversibility. The independent package audit passed once: `native-presentation-package-045-independent/result.json`. Exactly init/bootstrap/fresh scratch differ from 044; 666 payloads and all archive metadata are preserved. The three-member overlay is **701039 bytes**, SHA-256 `18d21887be15c02d15dde6b4fcaf8250e0dba1b755fcec3abd7a9c2511909d09`; the actual 043 GPU telemetry module is unchanged. All three original SDK images and prior 041/043/044/older evidence hashes passed independently.

No 045 installation or boot has occurred at this report's creation. Future staging/boot must retain the existing 64 MiB EFI reserve, single-attempt/return guards and original authentication; more complete capture alone will not establish 120 FPS.
