# OHOS Adreno/MSM build — 001 failure retained, 002 pending

## Scope

Prepare the real Freedreno Gallium driver for subsequent MateBook render-only testing, rather than mistaking the VM's softpipe rendering for native Adreno support. These are build-only operations in fresh private WSL directories. They do not run target code, access DRM devices, modeset, load a module, deploy a service or alter Ubuntu. No original SDK image is modified.

Both builders use existing local Mesa source `c185b4a7b0ff052f556dff1b3849a9c9c6115640` and the existing OHOS cross-toolchain, `--wrap-mode=nodownload`, `gallium-drivers=freedreno`, `freedreno-kmds=msm`, `allow-kcmp=enabled`, four build jobs and a private output bundle. No software fallback driver is requested. Introspection checks the selected driver/options; packaged files must be AArch64 and must not depend on glibc, libstdc++ or libgcc_s. Existing guarded build/source/toolchain files are rehashed before a successful result can be published. No install command is used.

## 001: actual compile failure

The first configuration succeeded, but Ninja command 1 failed in genuine A6xx sources including `fd6_blend.cc` and `fd6_const.cc`. Clang 19 rejects nonconstant C++17 list-initialization narrowing: unsigned blend flags to `bool`, and split 64-bit GPU-address values to 32-bit register words. The original compiler wrapper does not add a narrowing override; observed compiler flags include `-Wall -std=c++17`.

The failure and full diagnostics remain in `original-adreno-mesa-001-launch-output.txt` and `original-adreno-mesa-001/{commands.json,1.stdout.txt,1.stderr.txt}`. This completed operational build is not rerun or relabelled as passing.

## 002: narrow compiler compatibility change

A fresh builder adds **only** `-Wno-error=c++11-narrowing` to its own `cpp_args`. This retains these diagnostics as warnings, rather than suppressing them or disabling all warnings/errors. It does not edit shared Mesa sources, alter register expressions or fake any driver result. All other build and preservation gates remain intact. The compatibility choice must be considered when reviewing the eventual build logs; a successful compile would not establish runtime correctness.

Offline tests: first missing-builder failures were observed; the latest two explicit tests pass. Build 002 has been launched once; its result is pending at this report's creation. Runtime, device access, native service integration and physical display output remain unverified by these builds.

All three reference projects remain part of the porting route. Original service identities, authentication, SELinux support/permissive guest policy, watchdogs and freeze protections are unchanged. No MateBook SSH, Ubuntu boot/display/power change, download, subagent or commit was performed.
