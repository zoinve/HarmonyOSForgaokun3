# Original init graphics integration: 053–054

## Verified changes

- 053 changed only the virtual MMIO transport to modern VirtIO. The real kernel
  driver then bound the virtual GPU and registered genuine card0/renderD128
  (226:0/226:128). No fabricated device node or driver success stub was used.
- Both original composer and allocator VDIs were observed mapped in 053. Original
  RenderService/composer/allocator UIDs and SELinux domains were independently
  checked; 23 actual mode samples were permissive. Services still restarted and
  Foundation reported a critical fault. This is not graphics readiness.
- 054 added a RAM-only system overlay containing the reference EGL bridge and
  eight selected Mesa/dependency files. The vendor overlay still contains only
  the three provider002 files. Original services, credentials, native-window
  library and platform libc++ were not replaced.
- Original RenderService PIDs492 and1083 mapped the replacement EGL bridge,
  Mesa EGL/Gallium, private libc++_shared and the original platform libc++ at
  `/system/lib64/chipset-sdk-sp/libc++.so`. Composer VDI mapping was observed;
  **allocator VDI mapping was not captured in 054**. Do not infer it from 053.
- All 20 actual mode samples in 054 were permissive. Its guest rebooted at
  ~138.37 seconds after a Foundation critical fault; QEMU rc0 therefore is not a
  successful service/desktop exit. No boot-count or watchdog protection was removed.

## Actual crash evidence

Read-only `debugfs` extraction of the retained 054 scratch filesystem recovered
three original HiviewDFX reports, with scratch SHA-256 unchanged before/after:
`fde34e3ab8d940ecd4985ac5035dfda6a7046a418065bb39c10cbc1ab4400092`.

RenderService PIDs777,880,981 (UID1003) all crashed at original
`librender_service.z.so` PC0x40f378, Build ID
`2ceb723e313c80c3605ecd369c0b8cb6`:

`RSMainThread::SetFrameInfo` → `RSMainThread::OnVsync` → real VSync callback.

The reported fault is SIGSEGV at0xb2, with x19=0. This narrows the investigation
to actual original-service initialization/frame state. It does not establish why
the state is null, nor justify patching out the crash, faking initialization or
disabling the original service protections.

## Evidence and preservation

- `reports/original-graphics-boot-053-independent.json`
- `reports/original-graphics-boot-054-independent.json`
- `reports/original-graphics-crashes-054/result.json` and three raw crash logs.
- 054 serial548894 bytes, SHA-256
  `ba3fa71572b02cfe86e3e6aaa3976029ba858acf90e743dd25b59e442b8bc277`.
- 054 initrd SHA-256
  `888c18caf4a91f3fa9599599711fbdea0471cb80dd718b76f509b68ec9671cc1`.
- Independent checks rehashed all three original SDK images, the injected
  archive/provider bytes, virtual kernel and all378 previous native raw files.
- Explicit offline EGL tests:6 passed. Verification corrections retained actual
  evidence: 053 has23 rather than24 samples; 054 rebooted rather than timing out;
  054 has no captured allocator VDI mapping; literal C++ paths require regex
  escaping. These did not rerun either VM or alter its raw logs/results.

All operations here used local isolated TCG guests, readonly SDK drives, fresh
RAM scratch and no guest network/host filesystem share. No MateBook SSH, host
boot/security changes, physical scanout or desktop verification occurred.

## Next

Inspect the original faulting instructions and earlier graphics initialization
errors, then correct the demonstrated integration dependency. Keep the three
reference projects, original service identities, guest permissive policy and
immutable evidence; do not return to private-function tests as the main goal.
