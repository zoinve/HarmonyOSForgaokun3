# Native YUV/BLOB integration 074

## Scope and references

The objective remains the real original HarmonyOS desktop plus interaction on
MateBook E Go. This build is not proof of completion.
All three original pinned references in reference-three-projects-001.md remain
required: L410 adaptations supply the retained socket codec boundary and
device-specific NV12/NV21 helper example; HarmonyMac supplies the original own
RGB VDI/bridge; Linux Compatibility Platform's AnCo/Wayland path does not replace
the original service/allocator/RenderService path.

Additional upstream primary-source checkouts, read only:

| Local reference | Commit |
| --- | --- |
| openharmony-drivers-peripheral-074 | 448a669f3555f90d042e3f7dd02972a9478381da |
| openharmony-graphic-surface-074 | 75b372a572526e945203b633989836792ac9ebc7 |
| openharmony-av-codec-gitee-074 | 7ed395e1fc920c2cae2bd2834437c48eac5b8d6b |

The GitHub av_codec mirror checkout was empty; it supplied no evidence.
The Gitee checkout supplies the actual codec source.
Upstream surface_type.h identifies GRAPHIC_PIXEL_FMT_BLOB=38.
SurfaceBufferImpl::GetPlanesInfo copies ImagePlane.hStride to rowStride and
vStride to columnStride. The prior own RGB ImageLayout reversed those fields.
Upstream codec buffer_converter.cpp computes slice height using plane[1].offset
divided by buffer stride, consistent with a physical luma/chroma layout.
These supplemental upstream revisions establish source semantics, not binary
compatibility of every private function in the commercial userland.

## Implementation

commercial-linear-layout-074.h supplies bounded common geometry calculations:
four RGB formats, even-dimension NV12/NV21, and one-row BLOB byte buffers.
YUV uses 8-bpp dumb backing with height H+H/2, byte pitch from the real driver,
and chroma offset pitch*H. RGB retains its 32-bpp backing. BLOB does not receive
a fabricated image format and is explicitly refused by EGL image import.
Sizes are bounded to 256 MiB, all plane ends checked, and original expectedSize
and protected-buffer rejection remain enforced. RegisterBuffer/Mmap/import
also check actual FD backing size before use.

GetImageLayout reports physical Y and interleaved chroma planes with row pitch
and column increments 1/2 respectively. RGB returns row pitch/column increment
4; BLOB returns row pitch/column increment 1. No allocator success is fabricated.
The native image bridge maps NV12/NV21 to corresponding DRM fourcc codes and
passes plane 0 and plane 1 FD/offset/pitch to real Mesa eglCreateImageKHR.
RGB window rendering/copy predicates are unchanged. No new color metadata is
invented and no original authentication or service definition is changed.

## Tests and build artifacts

commercial-linear-layout-test-074-r2 passed GCC ASan/UBSan with real native
2160x1440, 2560x1440, 3120x2080 and 262160x1 request shapes, RGB regressions,
odd/invalid dimensions, short strides/backing and overflow boundaries.
commercial-yuv-backend-test-074-r3 executes the actual transformed allocator
and image-attribute code, with explicitly mocked DRM and real memfd mmap.
Seven formats, repeated mappings, two-plane attributes, row/column strides,
short backing, protected rejection, expectedSize and four failure cleanup
branches pass ASan/UBSan; all fixture FDs are closed. This is NOT GPU evidence.
Earlier fixture compile failures are preserved separately.

commercial-yuv-074-r3 contains both aarch64 OHOS shared libraries linked only
against original commercial libc/libc++ runtime closures. EGL public dynamic
exports are identical to 067. The first build was rejected for two unwanted
C++ template exports; a fixed 19-element attribute array removes them. r2
compiled YUV; r3 adds the independently confirmed BLOB geometry. All retained.

## Native deployment guards

The candidate archive changes init/bootstrap and adds only allocator074/egl074
directories and their own libraries. EGL replaces both original integration
copies (system library directory and vendor passthrough) in read-only RAM
overlays. Other existing members, original codec helper/resources and service
identities remain unchanged. Existing 073 public request/service metadata
observation is retained; its trace/marker names intentionally remain 073.

Incremental chain: 001 -> 017 -> 016 -> 072 XZ -> 073 -> 074.
074 overlay: 770957 bytes, SHA-256
765f4cd6cb5ed23dfde51dbdc8e2464d9dde456066538591fe2aa509d81e4281.
Installation must verify exact parent hashes, archive delta and original guard
conditions; retention keeps only latest two entry files, never deletes shared
payloads. Native allocation, decoded frames, real GPU import, desktop pixels
and interaction remain unproven until the device evidence demonstrates them.

See commercial073-usage-and-format-correction.md before interpreting 073 usage
values: actual YUV usage is 0x40b, not the manual closure's erroneous 0x1035.
