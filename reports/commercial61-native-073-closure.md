# Native 073 closure

## Result

Real native desktop and interaction remain unverified. Do not rerun 073.
Run: `commercial61-native-073-0e92c8d1-0b6b-43e3-b338-70d7cf1ee53d`.
Started 2026-11-15 01:27:26 UTC; Ubuntu online at 01:31:08 UTC.
The original bounded target deadline and observer stop were recovered.
67 evidence files passed remote/local byte counts and SHA-256 checks.

## Newly established allocation boundary

`commercial61-native-073/allocator-analysis.json` contains 63 public AllocMem
requests from original allocator_host UID 3041. Requests include:

| Count | Width | Height | Format | Usage | Expected bytes |
| --- | --- | --- | --- | --- | --- |
| 46 | 2560 | 1600 | 12 | 0x1800 | 0 |
| 1 | 2160 | 1440 | 24 | 0x1035 | 0 |
| 6 | 2560 | 1440 | 24 | 0x1035 | 0 |
| 2 | 3120 | 2080 | 25 | 0x1035 | 0 |
| 2 | 262160 | 1 | 38 | 0x43 | 0 |
| 4 | 3120 | 2080 | 12 | 0x43 | 0 |
| 2 | 64 | 64 | 12 | 0x1035 | 0 |

Reference display_type.h identifies 24 as YCBCR_420_SP (NV12), 25 as
YCRCB_420_SP (NV21), and 12 as RGBA_8888. Format 38 is not defined in that
reference header; its meaning must not be invented.
The exact rebuilt allocator preserves the four-RGB-only supported() predicate;
therefore it rejects 24, 25 and 38. Its dimension guard also rejects width
262160. The request trace does not itself record return codes or caller stack:
do not claim an exact one-to-one correspondence with individual hilog failures.
Original-service hilog still records buffer allocation failures.

Public maps capture original allocator_host, av_codec_service UID 1013, and
the own VDI mapping `/vendor/lib64/libdisplay_buffer_vdi_impl.z.so`.
Both software helpers remain present at samples 8, 12, 18 and 28 (PIDs 607,
617). Global and service-root helper logs end in SOFTWARE_CODEC_READY; no
native decoded-frame proof was recovered. The previous app-root ENOENT is not
evidence of a missing global helper log.

## Pixels and rendering

Complete source 2560x1600 and output 1600x2560 frames are unchanged from 072.
Each contains 4,096,000 pixels, 4,091,348 black and 4,652 nonblack.
Source SHA-256: `7ec03e269b0b326237d07deffeb89c656691e4b696bf362075566c4f83f1b0a4`.
Output SHA-256: `11cfdd1750f4b2267c99bdc56f306f877cf7c1637e30073e4967579fcf2af0f3`.
Clockwise source-to-output differing pixels: zero.
First original render flush: 105.954 guest seconds; 48 subsequent frame records,
last at 153.864244 seconds. These are not desktop or interaction proof.
212 execute-only hardware breakpoint attachments, zero attachment failures,
lost samples, malformed records or instruction-pointer mismatches.

## Build and preservation

WSL Debian restart restored command execution. No partial allocator073 build
was present before starting this build. The own allocator compiled against the
original commercial runtime; SHA-256:
`9fc5473f5f7ac0e25239b6b610693daa5c240deb888875c457622fbe1c379687`.
The first logger test failed at linking because local Clang ASan runtime files
were missing. Its artifacts are retained. GCC ASan/UBSan r2 passed all three
cases, four-thread 128-record bound, errno preservation, missing-file refusal
and symlink refusal. No test fixture was substituted for native admission.

The incremental overlay is 734,611 bytes, SHA-256:
`f1057c054120d05feb3fdac9faccdb0c4de47c2d705ba0e4f0bb6f6245706082`.
Its verified chain is 001 -> 017 -> 016 -> shared 072 XZ -> 073.
Only init/bootstrap changed; the own observation VDI directory/library were
added. Original resource payloads and real software codec backend are unchanged.

Post-return verification confirms Ubuntu current/default, original firmware and
four source image hashes unchanged, screen-off timer enabled/active, lab
partition unmounted and original manual entry retained. The 071 entry was
archived and hash-verified before removal; latest experimental entries are
072/073. Shared payloads were not deleted.
Ubuntu boot ID: `a1f79ac4-7cb6-4428-be7a-41587e3cd56c`.

## Next implementation

Implement genuine NV12/NV21 backing sizes and byte strides, truthful image
plane layouts, mapper validation and existing Mesa import support together.
Do not merely relax supported(), return success, reinterpret YUV as RGB, or
claim decoded output without actual frames. Preserve RGB behavior.

Use all three pinned references from `reference-three-projects-001.md`:
L410 adaptations provide socket video adapters and a device-specific NV12/NV21
composer/helper example; their Mali/ION implementation is not an MSM allocator.
HarmonyMac's own VDI is the current RGB-only starting point, not a complete
YUV implementation. Linux Compatibility Platform's AnCo/Wayland application
integration is not a replacement for original HarmonyOS rendering or allocation.
