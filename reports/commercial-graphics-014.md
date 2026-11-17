# Commercial desktop: offline graphics closure through 014

The requested commercial desktop is **not yet working**. No 009–014 build was installed or booted. The last commercial test, 008, was recovered by the user manually; its network-return record is not evidence of automatic reboot.

## What was verified

- 008's sandbox path alias allowed the original SA 511 installer to start. Original SceneBoard installation subsequently reported success, but no running desktop was established. Later installation/database operations exhausted the 3 GiB guest data filesystem.
- 010 provides an 8 GiB fresh data filesystem guarded by actual boot-time memory admission: at least 15 GiB total RAM and 11 GiB available. An independent private WSL filesystem copy passed the actual mounted ext4 online-resize ioctl; this is not proof that the MateBook satisfies the RAM budget. No original image was resized.
- 010 bounds final snapshot/flush/unmount work to 15 seconds, avoids the final unbounded global sync, and retains a separate 210-second software deadline. Target execution is limited to 90 seconds. A wedged kernel or shutdown path cannot be guaranteed recoverable by a software watchdog; incomplete evidence remains possible after a timeout.
- The old graphics bundle required the SDK's `libc++_shared.so`, so it was not reused as the commercial runtime. Own Mesa 25.0.1/Freedreno was rebuilt in 013 against the ISO's actual `libc.so` and `libc++.so`. The ELF dependency and C++ symbol gates passed. Compiler headers and static compiler support are build tools, not replacement SDK system services or shared runtimes.
- 014 rebuilds the project's own EGL bridge and display-composer provider against that same original commercial runtime and points both to the new private Mesa directory `/system/lib64/lab-commercial013/`. Both compiled with undefined-symbol rejection and passed artifact/link-trace checks. Original commercial system services remain untouched.

The failed 011/012 feature-detection builds and their logs are retained. 013 only supplies a missing declaration for the **existing original** `secure_getenv` function; its implementation and security semantics were not replaced.

## Remaining acceptance

These are offline build/provenance checks, not proof of commercial HDI 1.3 ABI compatibility, original RenderService backend selection, loader-namespace access, physical scanout, input, or a running SceneBoard. The original L410 RenderService wrapper still selects an incompatible Mali Vulkan backend; hardware integration must select the real FD690 path without identity shims or fabricated success.

Fresh SSH attempts to the MateBook at its configured address timed out. Consequently neither current memory/storage admission nor target loading/display could be verified, and **no further reboot was attempted**. Restore Ubuntu network/SSH access before deployment. Preserve Ubuntu default startup, original ISO/images, numbered evidence, and the user's persistently disabled experimental screen-off timer.

## Evidence

- `reports/commercial61-native-008/manual-recovery-analysis.json`
- `reports/commercial61-native-010/filesystem-verification.json`
- `reports/commercial-mesa-013/result.json`
- `reports/commercial-graphics-014/result.json`
- `reports/commercial-graphics-014/nativewindow-export-audit.json`

014 composer SHA256: `31de3d40703ed457e1e2e4420dd3e8e37be87a62820a422a72d61798ea6f3a38`.

014 EGL bridge SHA256: `83de7308499d873466a90f84c1762ba9c57c2e7d87ba9403b5eab01c601f1e60`.
