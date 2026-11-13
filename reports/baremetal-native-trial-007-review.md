# Trial007: native kernel and OHOS Freedreno joint verification

Diagnostic010 booted profile003's native kernel on the MateBook and returned to Ubuntu. This is the first verified GPU run combining our native kernel with the unchanged OHOS Mesa/runtime bundle, rather than the previous Ubuntu-kernel GPU runs.

## Evidence

- All 226 collected raw files passed size/SHA-256 checks: 188 prior files and 38 new cumulative snapshots, not 38 independent tests. Final `phase-038.log` SHA-256: `97672cce6f88a65918c75b577ced74024409a442fc7155575f35ba20ebbc7983`. Its device-tree NUL remains untouched.
- Native kernel SHA-256 `4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`; diagnostic archive SHA-256 `f00ae673e495abbd521628418badbc16d7f12d72d40236855b0a7f149e0e5afb`.
- Read-only identity probe passed: traditional Binder protocol8/features5, active SELinux and initial enforcing1, zero task identities, no token/permission changes. No SELinux policy was loaded by the diagnostic.
- Display enumeration retained card0/renderD128, DSI-1 connected with 1600x2560 modes, and Himax input2/event2 registration. All 13 explicit module requests and enumeration completed with status0.
- Offscreen GPU phase completed with status0. Actual sandbox UID/GID65534, no supplementary groups/capabilities, no-new-privileges and private namespaces were reported before the unchanged OHOS loader executed the original fence probe.
- Actual renderer FD690, EGL1.5/OpenGL ES3.2 Mesa25.0.1; linear 16x16 GBM buffer, stride256, offset0/modifier0. Shader readback returned opaque red `(255,0,0,255)` and blue `(0,0,255,255)`.
- Native fence export/poll/reimport completed; a second independently opened GBM device imported the DMA-BUF and CPU-mapped the same expected pixels. `FENCE001_PASS` and `NATIVE_MESA001_END status=0` were captured.

The remaining `os_same_file_description` warning and its same-description fallback are preserved. This successful path is not proof of general FD-identity compatibility, stress stability, physical scanout, actual touch interaction, a loaded-policy authorization test, or a HarmonyOS desktop. All desktop verification markers remain zero.

## Return and preservation

Returned Ubuntu kernel `7.1.0-rc3-gaokun3+`, boot ID `6c8229ac-31cf-4ac6-9de7-3794b3f7d1eb`. SSH observation began immediately; the new Ubuntu boot was observed after approximately 62.35 seconds, not an exact measured boot duration.

Independent verification confirmed Ubuntu's persistent default, absent one-shot, all raw hashes, enabled/active screen-off timer and GDM already logically off. The verifier forbids display setters; physical screen state was not observed.

The only tracked pre-existing EFI byte change across reboot was `loader/random-seed`, from `c35143c247d558f3b7f8832debd3d5417629d6e61d10341368ee0d4dcf4eb720` to `935fa1731563a8798efd49948c3517117294e245b12dbd44a9f30542bd1bc4dc`. Preserve the fresh seed; do not restore stale entropy or claim every EFI file stayed byte-identical across reboot.

Authoritative machine-readable evidence: `baremetal-native-trial-007-mesa-verification.json`, `baremetal-native-trial-007-independent-verification.json`, and the immutable collected raw files. Cleanup of the consumed010 configuration is separately archived and verified, not removal of diagnostic assets or logs.

Cleanup004 completed: only `loader/entries/harmony-native-diag-010+0-1.conf` was removed after matching local/remote archived SHA-256 `563ba833c901fa7525ab31e8e190cef29c8535b7caabf82c7280a4e858e76052`. All 79 other EFI files, persistent Ubuntu default and firmware entries remained unchanged; no reboot or asset/log removal occurred. See `boot-entry-cleanup-004.json`. Future preflights must use the post-cleanup baseline.
