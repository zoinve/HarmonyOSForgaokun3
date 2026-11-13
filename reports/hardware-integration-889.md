# 889: product GLES dispatch comparison

Same native ARM/KVM, VirGL/FD690, unchanged product EGL/GLES frontend, RAM-only Mesa/NativeWindow bridge, 1920×1080, physical display off.

- Direct bridge: current GLES context, `virgl (FD690)`, green framebuffer readback passed.
- Product EGL frontend: initialization, configuration, context creation, make-current and current-context/client-version queries passed.
- Product `eglGetProcAddress("glGetString")` resolves to original `libGLESv3.so`, but returns NULL.
- Direct Mesa `glGetString` in that same current context returns `virgl (FD690)`.
- Product probe correctly fails rather than weakening its renderer/pixel checks.
- QMP remains running; screenshot reports `no surface`. No desktop verified.

Next diagnostic 890 only inspects the standalone diagnostic thread's product hook table/key and function provenance. Rendering libraries and original product frontend remain unchanged. Immutable payload SHA-256: `3bbc7ff684105786d48680bb1335821772ab23cb7f5f1edc98b5dc983f28fc80`. Actual archive executable-mode check passed.

889 was stopped gracefully. Final original-image integrity checks and scoped userdata cleanup are recorded separately after runner completion.
