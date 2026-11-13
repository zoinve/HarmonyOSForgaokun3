# Current verified status — trial010

- **Native board, own kernel:** traditional Binder protocol8/features5; active SELinux with initial enforcing1 but **no policy loaded by diagnostics**; display connector1600×2560 and touchscreen registration retained.
- **Native GPU:** OHOS Mesa/Freedreno FD690 offscreen rendering, native fence export/import and independent GBM DMA-BUF readback passed in earlier trial008; corrected FD-identity code passed without the old warning.
- **Native allocator:** trial010 now passes actual original-SDK56-byte BufferHandle allocation and render-only copied VDI CPU↔GPU coherence at13×7 and1600×2560. Synchronization used glFinish; this is not asynchronous/cross-process or full composer proof.
- **Separate QEMU scope:** original SDK init starts genuine services and SAMGR answers an allowed Binder ping with its authentic native token under its own selected developer policy/enforcing1. Privileged service queries from the zero-token observer were legitimately rejected and were not bypassed. Earlier full original-SDK IPC callback tests ran without active SELinux; do not merge those scopes.
- **Preservation:** all302 raw files verified, Ubuntu returned with its original persistent default, automatic logical screen-off verified without setters. Cleanup007 archived the consumed013 config, then removed only that entry; assets/logs remain. Original SDK images and Ubuntu libraries/data are unchanged.

**Still unverified:** full bare-metal HarmonyOS init/service graph, compositor integration, physical scanout/touch interaction and HarmonyOS desktop. Next offscreen boundary is cross-process buffer/FD ownership and explicit synchronization before compositor integration; do not switch display modes or claim desktop readiness from allocator pixels.

Detailed evidence: `baremetal-native-trial-010-review.md`, `baremetal-native-trial-010-independent-verification.json`, `boot-entry-cleanup-007.json`. Reference provenance remains HarmonyMac confirmed; the second user-provided project is not yet identified and is not claimed reviewed.
