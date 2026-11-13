# 891: product EGL/GLES hardware readback verified

Both the direct NativeWindow bridge and the unchanged product EGL/GLES frontend returned `virgl (FD690)` and passed the green-pixel framebuffer readback. The product GLES wrapper's hook-table entry now resolves to the real Mesa GLES driver rather than the old vendor implementation. Evidence: `next-experiment/diagnostic-891.txt`.

This verifies the product frontend's GPU context and drawing path, not the desktop or full-system presentation. QMP still reported `no surface`; no genuine desktop was observed. The unsupported recordable config attribute remains an explicitly reported diagnostic failure, not an advertised or fabricated capability.

Fresh payload 892 adds bounded, per-process EGL call logs under `/data/local/tmp/gpu892-<pid>.log`, preserving rendering behavior. It traces initialization, configuration, context creation, window creation, make-current and swap entry. Existing libraries, native GPU drawing and all protection mechanisms remain intact. Its archive SHA-256 is `8782f59e120363f6161819731a751ceb41f7d244f88a8e7af3f49fa0f7a228b1`; executable-mode validation passed. No 892 guest has been launched yet.

891 was stopped gracefully; post-run integrity results are recorded separately when its runner completes. Physical viewing remains disabled.
