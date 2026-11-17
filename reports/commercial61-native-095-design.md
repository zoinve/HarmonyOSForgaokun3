# Native 095: one normal OOBE window-close request

## Scope

Retain the original 094 early genuine hardware inputs, identity helper, network
refresh and exact original/own startup cores. Add only a diagnostic shell worker,
WM table checker and Linux input-event helper. The original guide, SceneBoard,
system services, packages, permissions, callbacks, watchdogs, identities and
provisioning records are not modified. This is not commercial activation.

At monotonic time 125 seconds the worker accepts only one live SceneBoard PID
and one live OOBE PID. It checks the helper/checker hashes, reads original WMS
output with a two-second bound, and requires a unique focused display-0 type-1
`hwstartupguide` window belonging to that OOBE PID. It rechecks both process IDs
before sending a single Alt+F4 chord through the exact original keyboard device.
It refuses if any physical key is held. Writes are nonblocking and both release
events are attempted even after a write failure. No repeated close/force-stop is
performed; the original WM/guide may reject or handle the request normally.

Focus verification is a snapshot, not an atomic lock on original WM state. Native
logs must establish the actual recipient and resulting lifecycle; successful
event writes alone are not a closed guide or a desktop.

The unchanged inherited core sends LEFTMETA at 132 seconds. The new worker dumps
original WMS state at 130 and 140 seconds. Existing full-frame captures and final
diagnostic snapshot are retained. Its inherited 087/075/093 labels remain genuine.

## Verification Before Boot

- Host/AArch64 helper byte-sequence, invalid invocation and rejected-write tests.
- Twelve focus-table cases under the packaged AArch64 BusyBox; actual runtime
  `/system/bin/awk` is the original toybox applet, so runtime execution is still
  required. Failure of that applet is fail-closed.
- Ten complete shell control-flow fixtures, including wrong focus, ambiguous
  processes, PID change, expired deadline, hash mismatch and failed dump/helper.
- Full ordered initrd chain equals the full 095 RAM archive. Only the existing
  desktop diagnostic script and three declared new diagnostic files differ.
- Overlay: 296,519 bytes, SHA-256
  `5475a4544dec3c3b62d4ce49fb93912573450b2e2ba9db4605dcc26eb32ca429`.
- Unreferenced old 048 initrd archived with verified hashes in cleanup 003;
  156 other EFI files unchanged. No referenced payload was removed.
- Installed entry 095; retention archives old entry 092, keeping 094/095, Ubuntu
  default and original manual entry. All shared chain payloads remain.

## Acceptance

Require the recovered native event/lifecycle records, full-resolution pixels and
a visible interactive native desktop, not merely an absent guide PID, successful
close request, tests passing, or OCR silence. Preserve original privacy export
guards and require post-return image/EFI/firmware/default/timer verification.
