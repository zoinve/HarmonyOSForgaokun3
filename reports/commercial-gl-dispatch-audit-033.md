# Commercial GL dispatch provenance correction

The previously inspected `original-egl-loader-001/libEGL.so` and `official-frontend-inspect-926/libGLESv3.so` are **not** the corresponding binaries from the current commercial image. Their addresses and table layouts must not be used as commercial ABI evidence. This correction does not change any closed boot's raw evidence or image contents.

Read-only `debugfs` extraction from `p111-system.kr990-ext4-v1.img` established:

| Commercial image file | Bytes | SHA256 |
|---|---:|---|
| `/system/lib64/libEGL.so` | 433384 | `f7d741c9f11eda806b41686c873ddc255f68b76b25c171835d892d72a3adb060` |
| `/system/lib64/libGLESv3.so` | 342576 | `ba42e9b8094b9512c3d2e8eb1677c2ab9f42eedad7b9f73b4125187fd164f8b0` |

`/system/lib64/libGLESv2.so` was not present at that exact path. The extracted binaries and exclusive provenance manifest reside in the WSL `commercial-gl-dispatch-audit-033-r2` directory. Earlier incomplete audit directories remain preserved; no source image was written.

Actual commercial disassembly shows normal GL driver loading via provider `dlsym`, then its EGL get-procedure-address fallback, and GL thread-table installation after successful real `MakeCurrent`. It does not establish that runtime function pointers or current GL state are correct. The release-source “There is just no current context. skip” message is an already-unbound release path and alone is not evidence of rendering failure.

The next narrow hypothesis is a mismatch between what the original public GLES frontend and the own Mesa provider see on the same original RenderService swap thread. Observe public version/renderer, read/draw FBO, current program, viewport and context presence on both routes. Do not read private table offsets, replace the original frontend, alter hooks or fabricate success. Original frontend and Mesa context pointers are different object layers and are not expected to compare equal.
