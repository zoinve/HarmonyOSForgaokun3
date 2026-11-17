# Native diagnostic sidecar 157: root guard refusal

Single boot `commercial61-native-087-846ed316-ecaa-47b8-b854-ea60f7c640bc`
returned to Ubuntu at 05:20:06 UTC on November 16, 2026.
All 187 retrieved files matched remote hashes and were rehashed for analysis.

## Result

No live authenticated native connection was verified. The client recorded
connection timeouts; these alone do not establish a network or firewall cause.

The latest phase log proves a more immediate failure:

- Line 1664: verified tools package loaded successfully, `LIVE157_LOAD status=0`.
- Line 90275: helper started, supervisor 3978, target 499.
- Line 300168: helper reaped, wait status 20224, which is normal exit code 79.
- Launcher 157 returns 79 before namespace creation when its original-init
  path verification fails. No namespace context or server-spawn marker occurred.

The runtime source `bootstrap-runtime087.c:1055` creates `/system` as an absolute
symlink to `/usr/system`. Directly following
`/proc/<target>/root/system/bin/init` from the external caller does not anchor
that absolute link in the target root. The check used the wrong resolution
semantics. Original network observers independently entered target 499's root
and reported the expected separate network namespace, inode 4026533332.

Correction 158 uses an opened target-root directory and `openat2` with
`RESOLVE_IN_ROOT | RESOLVE_NO_MAGICLINKS`, retaining original inode/type
verification and refusing unsupported or escaping resolution. It does not
join the original mount namespace or weaken HDC, signature or identity checks.
Its independent regression fixture reproduces the absolute-symlink layout.
Do not rerun 157 or overwrite its negative result.

## Baseline and preservation

- Original MMI still holds the touchscreen; storage modules remain live.
  Physical touch/USB service acceptance remains unverified.
- Ubuntu current/default and firmware passed preservation verification.
- 176 prior EFI files unchanged except the normal boot-managed random seed;
  the old 152 entry removal was explicitly authorized and archived.
- All four original HarmonyOS images retained their exact hashes.
- LAB was unmounted; screen-off timer enabled/active; original manual entry retained.
- Ubuntu return boot ID: `11ebd438-9365-46fe-a5ae-e243b6fcae5e`.

Machine-readable result: `commercial61-native-157/live-runtime-analysis-157.json`.
