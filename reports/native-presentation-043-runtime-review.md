# Native 043 — verified return, but no accepted presentation window

## Actual single-run result

- Exactly one counted diagnostic boot; the return probe began immediately, first rejected the unchanged Ubuntu boot, and accepted the changed Ubuntu boot after 309.28845 seconds / 78 attempts. Returned boot ID: `23d7ecf4-a2da-4c8f-87ba-dde41c90c5a7`; kernel `7.1.0-rc3-gaokun3+`.
- Collected 71 genuine raw files, 240,820,788 bytes, with remote/local hashes matched. The first collector refused an 81,132,855-byte HiLog file at its 64 MiB per-file bound and unmounted the lab partition. Its failure remains preserved. Fresh attempt 002 permits **only** `interactive-hilog030.log` up to 128 MiB; other files remain capped at 64 MiB, total 512 MiB, 512 files, strict tar-path/type/hash checks. It succeeded without replaying the boot or filesystem journal.
- Independent return verification succeeded once: all 71 new raw files, 71 old 041 files, 378 older native files and three complete original SDK images match. Native EL2/043 overlay markers and 12 permissive SELinux observations are genuine. Ubuntu default, firmware, no pending one-shot, unmounted lab and automatic screen-off were verified; the observer made no `set-property` call. Physical screen observation is not claimed.
- All 102 pre-existing immutable EFI files remain unchanged. The own counted entry was consumed with unchanged content; only `loader/random-seed` otherwise changed, as expected after boot. Fresh entropy was preserved, not restored.

## What the graphics records actually establish

The raw final phase contains nine unique `NATIVE_PERF023` lines, including one real UID-3036 FD690 two-pass composition (`13641 us`), and 27 unique composer API records including one `Commit value=0`. `errno=22` alongside a successful return is not independently a failed Commit.

The only unique `NATIVE_PRESENT043` record is UID 3036 / PID 1054 clock metadata: `timestamp_monotonic=1`, no submission or completion. Initial `SetCrtc` is deliberately excluded. Consequently the analyzer has **zero accepted completed samples and no client completion-rate window**—not evidence that actual FPS was zero, and certainly not stable 120 FPS. Batched tails, finite observation and unchanged-content/idle periods remain sampling limits.

Authoritative outputs: `native-original-graphics-boot-043/post-return-verification.json`, `presentation-analysis.json`, `presentation043-journal.log`, and immutable `runtime-evidence`. Journal SHA-256: `d167b58e33cebd5caaf0fcc45774550dab5d2a95a5dc1ef75b4b75e6e1eb91c4`.

## Concrete startup blocker, not a permission workaround

`interactive-hilog030.log:73346–73350` reports original AppSpawn `mkdir` failures with `errno 30` (`EROFS`) under `/mnt/sandbox/100/com.ohos.sceneboard_preunlock/data/storage/el2`, `el3`, and `el4`. Lines 73390–73421 report the child failing its original sandbox mount/configuration. Foundation records actual `NotifyStartProcessFailed` requests. No SceneBoard-ready or sustained desktop workload is established by this run.

Frozen `bootstrap.c:768` creates `/mnt` and sandbox directories but never mounts a separate `/mnt` tmpfs. Read-only inspection of the genuine, hash-pinned `init_early` establishes its original `tmpfs /mnt`, `MS_NOSUID`, `mode=0755` mount at VA `0x23500`, then `MS_SLAVE` at `0x23520`. The unmodified original init remounts `/` read-only. This is a specific missing early-filesystem prerequisite; it does not justify disabling sandboxes, watchdogs, identity checks or authentication.

## Fresh 044 candidate, build and independent audit only

- Restores exactly that original `/mnt` setup before the existing sandbox aliases and original init. Checks real filesystem type, writable state, `nosuid`, mode 0755 and root ownership. Root read-only configuration, original services/identities/policy and GPU/telemetry module 043 remain untouched.
- Reversible source comparison removes only the new helper/include/call to recover byte-identical 043 bootstrap source. Outer init changes only the new run labels. All old files remain frozen.
- Fresh build and independent audit succeeded once; two offline source/archive gates passed. Full archives preserve metadata and **666 of 669** payloads against 043. Only init, bootstrap and fresh scratch contents differ. The small overlay contains init, bootstrap and the unchanged telemetry VDI; it reuses original base-032 scratch, not the newly formatted full-candidate scratch.
- Overlay: 699,477 bytes, SHA-256 `1c4aa6a12e636430f7892a709fd60ef1fd133df4bb55ac3ea0624d1b3c3d29d1`. Three complete SDK images and 71 old 041 + 71 new 043 + 378 older native raw files independently reverified unchanged.
- Evidence: `native-presentation-package-044-independent/result.json`. **Not installed or booted at this report's creation.** No 044 runtime, desktop/FPS or physical-input acceptance is inferred from a build.

No original identities, permissions, app sandboxes, login checks, watchdogs or screen-off policy were bypassed. No synthetic input was injected. One empty mountpoint from the refused first collector remains harmlessly unmounted; no broad cleanup or old experiment replay was performed.
