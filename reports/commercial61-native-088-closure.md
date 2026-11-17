# Experiment 088 closure

Distinct entry 088 reused core 087 without changing its raw run labels.
Run: `commercial61-native-087-0e604235-1c6d-40c2-bd2c-d5d70af5e429`.
All 131 retrieved files matched remote sizes and hashes.

The SceneBoard-only canonical config mount works. PID 4685 sees both workspace
paths, each mode 0644, 272 bytes, SHA256
`dfe636ad913da8ee3d43720e78c64e3df22b78e24addbdc21aa89cfde6d881ab`.
Original logs read one layout item and complete Dock initialization at
14:50:19.978 on 2026-11-15. Only one SceneBoard PID was observed.

OOBE remains: original guide PID 6614 reported an 8000 ms validation timeout.
Independent HTTP returned 204; HTTPS exited 60, TLS verification result 9.
The previous summary's claim of successful HTTPS for this run is not supported.
No certificate checks were bypassed. Credential secrecy comparison passed.

One complete 3S freeze capture (272497 bytes, SHA256
`6568b0c8e099e50bfa1e1188d8621c4b1df9ec6a46b06e260cb05b2236266420`)
shows the main thread waiting in libcollabfwk_devicedetect_client,
libcfwk_devicepicker_client, and Js_GetTrustedDeviceListSync. This is not the
earlier missing-Dock-application lookup stack. The capture is not proof of a
permanent hang or complete stability.
Original logs subsequently report this call returning zero devices with ret 0
at 14:50:33.355. The wait recovered.

The raw diagnostic successfully reads const.cust.config_dir_layer with exit 0:
`/usr/system:/usr/system/variant/pc/base:/usr/system/variant/pc/china:/vendor:/sys_prod:/chip_prod`.
The initial analyzer missed the begin marker because the preceding SELinux
context includes a NUL and no newline; its null parsed value is not a failed
parameter read.

Both full-resolution captures are complete. OCR is inconclusive and is not
visual desktop verification. UITest did not produce a permitted layout dump.
Neither stable desktop nor interaction is established. No OOBE stop was requested
in this observation-only run.

Serial preservation verification passed: Ubuntu current/default, 149 prior EFI
files unchanged, firmware and four original image hashes unchanged, lab
partition unmounted, screen-off timer enabled/active, manual entry retained.
Authorized archived entry 086 was removed; entries 087/088 retained.

Next hypothesis: with Dock configuration repaired and no observed SceneBoard
restart, use the reference's original aa force-stop once, gated on genuine Dock
initialization and survival of the same SceneBoard process. Do not fabricate
provisioning state or repeatedly kill the guide.
