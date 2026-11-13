# Native trial011: cross-process DMA-BUF and native fence

Candidate014 booted the profile003 native kernel (`4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`) and returned to Ubuntu `7.1.0-rc3-gaokun3+`, boot ID `44bc5a0b-8574-4864-8ba1-ef44c6d9be7a`. This is not a HarmonyOS desktop boot.

## Independently checked evidence

All 340 collected raw files match their recorded sizes and SHA-256 hashes. There are 38 new cumulative snapshots, not 38 independent tests. The final snapshot is `native-diag-001-249dd33a-36b4-41cc-86c5-d1e6cb34f1d9/phase-038.log`, 82,530 bytes, SHA-256 `e1f631e77ed7f940b15aec9fa62d8ad3fc057cafc3c6e575547a14fb61570062`. Its device-tree NUL is preserved.

All recorded phase-end statuses are zero. The unchanged identity helper reports Binder protocol8/features5, legacy Binder, active SELinux and initial enforcing1, with no token or permission modifications and no policy loaded by the probe.

## Actual native GPU result

The original OHOS runtime and Mesa003 libraries ran in the unchanged private launcher: UID/GID65534, no supplementary groups or capabilities, NNP1, private PID/mount/network namespaces, render-node access and no primary DRM node.

- FD690, EGL1.5, GLES3.2 Mesa25.0.1; linear ARGB8888, 16×16, stride256, offset0.
- Producer PID1 and a separately executed consumer PID2 transferred real DMA-BUF and sync_file descriptors through private SCM_RIGHTS messaging.
- The producer closed its two transfer duplicates. The consumer polled the received fence, independently opened/imported through GBM, then closed the received DMA-BUF descriptor after import.
- Consumer pixels were exact opaque red `255,0,0,255` and blue `0,0,255,255`.
- Producer fence polling, EGL fence reimport, GPU readback and another independent GBM mapping also passed with exact pixels.
- `IPC002_PASS cross_process_dmabuf_and_native_fence desktop_not_tested=1`; launcher and GPU phase status0.

This extends the earlier Ubuntu-only IPC result to the actual native candidate kernel. It does not establish an initially unsignaled fence, general HDI serialization, all formats or dimensions, a compositor, physical scanout, touch interaction, full services, or GPU authorization under a loaded SELinux policy.

## Return and preservation

`baremetal-native-trial-011-independent-verification.json` verifies the changed Ubuntu boot, all 340 raw hashes, unchanged persistent Ubuntu default, absent one-shot selection, and active screen-off timer. The active GDM session was already logically off; the verifier refuses display setters and did not change screen state. Physical screen state was not observed.

The only tracked pre-existing EFI file change across reboot was `loader/random-seed`, from `198cacf054b22b1ff1badc4204a1416033e86c3b7f3eff71ad6b90e80e2a2674` to `68b420fb265c0c8c11437fcdc08d594cb66630c9eb4784ec94b5d8bede06d7fa`. Do not restore stale entropy or describe all EFI bytes as unchanged after reboot.

Cleanup008 stopped before remote archival or removal because its independent candidate-set guard still named013; its local backup and failure are retained. Fresh cleanup009 corrected only that guard and its output namespace. Before execution, AST-only validation checked both candidate014 guards and all340-log admission; no generated launcher was executed during preflight.

Cleanup009 succeeded: the exact consumed014 configuration (SHA-256 `2ad43291cda7bc725c0c9654ee979e2ec083ccd3a383a741f34009551bab0d55`) was archived locally and under `/var/lib/harmony-lab-boot-entry-cleanup-009` before removing only `loader/entries/harmony-native-diag-014+0-1.conf`. All82 other EFI files were byte-identical; Ubuntu default and firmware entries remained unchanged. No additional reboot occurred, and candidate assets and raw logs remain retained. Future installation guards must use a fresh post-cleanup baseline.
