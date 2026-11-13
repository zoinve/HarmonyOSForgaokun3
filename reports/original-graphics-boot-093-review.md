# Original graphical boot 093 — actual AppSpawn filesystem failure

## Verified outcome

- Original AppSpawn PID 1652 was queried at samples 41, 49 and 61. All six original HiLog invocations exited normally; this does not establish application-start success.
- The daemon's genuine logs report `mkdir` failures with **errno 30 (`EROFS`)** at `/mnt/sandbox/100/com.ohos.sceneboard_preunlock/data/storage/el2`, `el3` and `el4`. SceneBoard spawn replies remain `218103816` (`0xd000008`). This numeric result has not been independently mapped to a specific hook; the preceding filesystem errors are concrete evidence, not proof that no additional failure exists.
- No sandbox switch, original caller identity, token, permission, signature or installation check was bypassed. AppSpawn's word “success” beside a nonzero reply is not business success. No desktop is verified.
- Independent evidence: `original-graphics-boot-093-independent.json`; serial SHA-256 `e1ff8d53f34d7d847af5ed66561e0320b3c6b267b9a8e6a372769d856b32dd1f`. All 12 injected provider files, real ashmem, query helper, initrd, kernel, three original SDK images and 378 earlier native evidence files passed the inherited checks. No Foundation critical fault or guest reboot was observed within the bounded run.

## Missing original early-mount prerequisite

Read-only inspection of the already extracted genuine `init_early.elf` verified SHA-256 `9b475fa2588d4a7f46995de26d61689ce1bb8f1b7ce2c4588fac00c244c94824` and these actual calls:

1. VA `0x23500`: `mount("tmpfs", "/mnt", "tmpfs", MS_NOSUID, "mode=0755")` (flags `2`).
2. VA `0x23520`: `mount(NULL, "/mnt", NULL, MS_SLAVE, NULL)` (flags `0x80000`; **slave**, not shared).

The previous bootstrap omitted a separate `/mnt` mount, while the unmodified original init config remounts `/` read-only. Restoring the original early mount is a focused filesystem-layout correction, not permission relaxation or disabling app sandboxes.

## Fresh candidate 094

- Adds only the guarded original `/mnt` tmpfs setup and passive root/`/mnt` mount-state observations. The mounted filesystem type, writable state, `nosuid`, root ownership and mode 0755 are checked before original init executes. The root read-only configuration remains untouched.
- Uses the same original services/profiles/policy/identities, providers 005, EGL/Mesa 009, real ashmem and virtual kernel 002; retains the canonical read-only `nodev` `/system` bind and private 8 GiB disk-backed test data.
- Offline checks: 094 suite **3 passed**, parent 093 suite **2 passed**. Preparation succeeded once; init 853,896 bytes, SHA-256 `3bfda3b921083fd62bf72f2afeb8d251b7bed433d0ab777714e9539c4fe1cca6`. Original policy and graphics init config hashes remain unchanged.
- Runtime and independent verification are pending at this report's creation. No application-start or pixel outcome is inferred from preparation.

All work remains local, isolated WSL/QEMU testing. No MateBook/Ubuntu boot, security, screen-off or physical-display changes were made. All three reference projects remain part of the porting route. Completed numbered experiments and their evidence were not rerun or overwritten.
