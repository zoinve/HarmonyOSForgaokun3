# Native HarmonyOS readiness: ABI audit 002

## Verified evidence

`baremetal-harmony-abi-audit-002.json` records fresh hashes of the candidate
kernel source, resolved configuration, retained original SDK libraries and local
reference implementation. All critical kernel source files match the staged
source manifest. This audit does not change kernel source or system images.

- The candidate enables standard Binder, binderfs and binder/hwbinder/vndbinder
  devices. It uses 4 KiB pages; the old VM's 4 KiB-on-larger-page adaptations
  must not be copied blindly.
- The candidate does not contain the named OHOS Binder identity interfaces
  `BINDER_FEATURE_SET`, `BINDER_GET_ACCESS_TOKEN` or `BINDER_GET_SENDER_INFO`,
  or the reference's `CONFIG_ACCESS_TOKENID` integration.
- The local reference driver implements access-token commands 1–8. Original
  SDK disassembly also shows parent-token command 9 and SPM commands 16–25;
  see `baremetal-sdk7-identity-abi-gap-001.md` for the complete observed list.
- Authoritative SDK 7 SPM payload, permission, concurrency and lifetime
  semantics have not been established from the retained materials.

## Decision

A full native HarmonyOS service boot is **not ready**. Applying an older
reference patch would not establish SDK 7 compatibility. No fabricated token
IDs, success stubs, permissive access checks or authentication database changes
will be used to conceal missing interfaces. Binder source-name checks are an
inventory, not an exhaustive ABI test or proof of which service would fail first.

Graphics can be developed independently: the 007 native Linux trial verified
MSM DRM device/connector enumeration and Himax input registration. An isolated
OHOS-targeted Freedreno EGL/GLES/GBM build is therefore the next useful step;
it does not imply that the HarmonyOS compositor or complete desktop can run.

## Mesa build evidence so far

Build 001 configured Mesa 25.0.1 for Freedreno/MSM using the existing OHOS
toolchain, with dependency downloads disabled. Compilation failed on Clang's
C++ narrowing diagnostics in A6xx register initializers. Its original result
remains unchanged, including the failed source-tree equality check.

`baremetal-mesa-freedreno-build-001/source-difference-audit.json` explains that
check: one Python bytecode cache was added; no pre-existing source file or
symlink was removed or changed. The legacy library prefix remained unchanged.
Build 002 uses a fresh directory, disables Python bytecode writes and adds only
the C++ compatibility flag `-Wno-c++11-narrowing`. Its result must be inspected
before claiming compilation success, and GPU execution requires a separate
off-screen renderer and pixel-readback test. Neither compilation nor such a
test would establish native HarmonyOS desktop readiness.

### Verified build 002 result

Build 002 completed configuration, compilation and DESTDIR staging successfully.
Its result records unchanged Mesa sources and legacy library prefix; an
independent follow-up checked all 34 staged regular files against recorded sizes
and SHA-256 hashes. Eight versioned library symlinks were also retained. The
artifacts are OHOS-targeted AArch64 Freedreno/MSM EGL/GLES/GBM libraries, not
installed replacements. GPU execution and pixel correctness remain separate
checks; the Binder/access-token readiness decision above is unchanged.

## Subsequent evidence — identity candidate 002, through test 012

The inventory above describes the original unpatched candidate, not the later
identity-enabled candidate. Subsequent work is recorded separately; it does not
rewrite the initial audit or establish full system readiness.

- Disassembly of the original SDK kernel established that access-token commands
  9 and 16–25 are unsupported there too, returning `EOPNOTSUPP`. The new driver
  preserves that error instead of fabricating undocumented SPM behavior.
- The isolated candidate implements the stock protocol-8 Binder identity
  extensions and feature mask 5. Real kernel tests cover denial paths, token
  inheritance, permission storage, synchronous/one-way transactions and nested
  replies. Original SDK libraries negotiate and use those interfaces.
- Test 012 additionally executes the original SDK's incoming callback dispatch,
  full caller-token/PID/UID reporting, and restoration of outside-transaction
  identity. See `baremetal-identity-sdk-callback-012-review.md`.
- Physical-board trial 005 verified the candidate's non-mutating identity
  interface checks while retaining DRM and Himax enumeration. Full original
  SDK transactions have so far been tested in the isolated ARM64 kernel, not
  in a complete HarmonyOS service boot on the board.
- OHOS Mesa off-screen hardware rendering, DMA-BUF sharing and native-fence
  tests subsequently passed on the board under Ubuntu; those are separate from
  HarmonyOS compositor integration.

The next boundary is the original minimal service environment, not another
guess at SPM semantics. Complete service authentication, boot, display scanout
and desktop readiness remain unverified.
# Subsequent SELinux activation finding (QEMU 013)

The candidate and its console-test configuration contain `CONFIG_SECURITY_SELINUX=y`, but their explicit default `CONFIG_LSM` value is `landlock,lockdown,yama,loadpin,safesetid,integrity,bpf`, which omits SELinux. `CONFIG_DEFAULT_SECURITY_SELINUX=y` does not override that explicit list. The isolated 013 boot had no SELinux initialization and could not obtain the SELinux sysfs mount point.

Consequently, earlier Binder/token and original-SDK IPC successes establish the recorded ABI behavior **without an active loaded SELinux policy**; they are not evidence of SELinux-enforcing service compatibility. Preserving that configuration was a preservation result, not proof that SELinux protection was active. QEMU 014 tests the identical kernel and unchanged production policy with SELinux explicitly added to the otherwise retained LSM list. No Ubuntu configuration or original image is changed.
