# 897: RenderService GPU contexts now work

The RAM-only graphics configuration removed only the three service-specific software driver overrides. Service identity, capabilities, permissions and all other configuration fields were preserved.

Actual observations (`next-experiment/diagnostic-897.txt`, remote serial log):

- RenderService now successfully creates a GBM device, EGL display and multiple real GLES contexts; this failed in 896.
- Bridge traces include NativeWindow creation, make-current and repeated swap-buffer calls.
- Both the independent bridge test and the original OHOS EGL/GLES frontend report `virgl (FD690)` and pass green pixel readback.
- QEMU remains running but screendump returns `no surface`. There is no verified desktop or full-system frame.

Fresh diagnostic payload 898 observes buffer request/copy/flush/swap return values and reads the real fbdev/DRM state. It does not change rendering returns, consume EGL errors, alter authentication or bypass drawing. SHA-256: `98341ef1e73793b3feb162538a3bd4af30585e16a7f21707615110233a7ae378`.

The screenshot failure is not interpreted as absence of GPU acceleration. 897 final original-image integrity checks are recorded separately after runner completion.
