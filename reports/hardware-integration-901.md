# GPU 901: NativeBuffer image imports fail

Native ARM/KVM, real host FD690 through VirGL, unchanged original OHOS EGL/GLES frontends. Both independent green-pixel tests still passed. This is not desktop evidence.

Actual RenderService trace repeatedly reported valid NativeBuffer handles (format 12, 1920×1080 or 512×512), followed by `GPU901_IMAGE_IMPORT result=0`. Early readbacks and the observed Composer client buffer were black. This establishes an image-import failure; it does not yet identify whether allocation, format, or another import requirement is responsible.

Read-only extraction of the original vendor `l410-graphics/allocator/libdmabufheap.z.so` shows an ION allocation interface. No original library was changed.

Fresh diagnostic payload 902 compares the original allocator, DRM dumb/PRIME and GBM buffers in independent probe processes, using real EGLImage import calls. It does not change any service allocator or weaken the existing pixel-test criteria. SHA-256: `118bffb6d0db959a3ffd95def6a21d1dcb2ed88d2a70ce59d33c56efc966b20a`.

901 was requested to quit gracefully. Its post-run original-image integrity results are recorded separately when available. No genuine desktop has been verified.
