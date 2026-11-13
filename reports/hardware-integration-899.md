# 899: Composer client state, not desktop

The hardware-rendering and NativeWindow request/copy/flush/swap checks still pass. The real 1920×1080 fbdev snapshot remains entirely black.

The preserved Composer has client fd 24, dimensions 1920×1080, stride 7680, format 12, and a mapped framebuffer. Its raw counters are retained in `next-experiment/diagnostic-899.txt`; their meaning is not inferred from unidentified offsets. Opening its DMA-BUF through `/proc/<pid>/fd/24` fails with ENXIO, so this experiment did not establish whether the source buffer contains an image.

Fresh payload 900 adds read-only diagnostics: RGB counts directly after the bridge's existing GPU readback, and an independent attempt to duplicate/map the Composer client fd using pidfd APIs. It does not change drawing, dispatch, service identity, authentication, or watchdogs. DMA-BUF CPU-cache synchronization is not requested by the observer, and any observed client-buffer result must retain that limitation.

Payload SHA-256: `2e60cdb711d6b1f7633d581a2bee25aa4f184d608596b6eb117fe9aae67ee1ef`. Its actual archive executable checks passed. No genuine desktop has been verified. Experiment 899 post-run integrity is reported separately after shutdown.
