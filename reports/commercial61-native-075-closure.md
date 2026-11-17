# Native 075: Real Input Delivered, Guide Dismissal Rejected

One run only: `commercial61-native-075-edef75aa-abd1-4064-a7cd-924ff12543b1`,
2026-11-15 02:15:54 to 02:19:35 UTC. All 73 evidence files authenticated.
Ubuntu returned with boot ID `3486f03d-3ff1-4778-a2e4-1b3864d398cb`.
The target timeout/exit and observer-stop records were recovered this time.
Ubuntu default/current boot, four immutable source images, original firmware,
enabled/active screen-off timer, manual entry and unmounted LAB partition all
passed the original post-return verifier.

The exact HarmonyMac commands were actually attempted: SceneBoard start at
58.12 seconds, guide force-stop ten seconds later. Both CLI invocations exited
0, but their text explicitly reports failure. The guide PID remains 6137 at
71.42 seconds; SceneBoard PID 4631 remains present. Exit code zero is not API
success. The public WMS dump also returned `request error`.

Authoritative hilog: line 208360 reports `dominate screen`, line 208361 reports
`caller invalid`; line 255632 reports invalid token, line 255648 denies
`ohos.permission.KILL_APP_PROCESSES`, and lines 255664-255666 deny background
cleanup and KillProcess. The caller was the pre-init diagnostic process with
UID 0 and SELinux context `kernel`, not a properly init-created diagnostic
service. Permissive SELinux does not grant an AccessToken permission. No
permission check was removed and no token was supplied.

Both complete source/scanout captures were exported successfully and validated
with zero rotation pixel differences. At 120 seconds, local OCR reads a network
not connected message. At 140 seconds, local OCR reads Quick Setup and a Skip
button. These remain OOBE pages, not the desktop. A LEFTMETA down/up sequence
at 132 seconds was written to the exact physical keyboard event6, 48 bytes each.
3,202,021 source pixels differ between captures, but video animation or user
input could explain this; causal desktop interaction is not established.

The exact second-export worker also passed compiled ASan/UBSan tests including
RGBA/BGRA stride, pixel preservation, distinct output names, no overwrite,
wrong owner, malformed marker, symlink and oversized-input rejection.

Unlike 074's early-only hilog, this boot includes later native codec errors:
the original HEVC adapter reports SendFrame decode errors. Do not infer native
decode completion from allocation success or helper readiness.

076 will request the needed permissions explicitly for a distinctly named
diagnostic service through original init configuration. Existing service
definitions/identities and all original checks remain intact. No claim of
desktop, activation or verified interactive desktop is made for 075.
