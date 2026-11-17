# Native Driver Run 130

User-confirmed desktop entry remains the baseline. This run only changed the
backlight implementation and a narrow permission rule, not OOBE or activation.

All 135 retrieved files matched their recorded hashes. The original service
requested backlight level 11363 and logged completion without the previous
SetDisplayBacklight failure. The real sysfs brightness node was verified and
given root:3036 mode 0660 before services; permission preparation did not write
brightness. Composer stderr GET/SET markers were not collected anywhere in the
retrieved evidence. Therefore original-service sysfs writes, readback, physical
luminance and slider interaction are NOT independently verified. A missing
error is not a successful hardware acceptance test.

Input analysis confirms keyboard delivery to original SceneBoard (one matched
48-event record), not visible interaction. The first full-resolution capture
was complete with nonblack content and exact clockwise scanout rotation. The
second-frame reader expected full-ready-075, absent from this run, and failed;
no second-frame result or stability claim is made.

Post-return checks passed: Ubuntu current/default, original manual entry,
enabled/active screen-off timer, original firmware and four original images.
166 prior EFI files are unchanged except the normal random seed and the
hash-archived, authorized removal of experimental entry 123. Entries 124/130
remain; shared payloads remain intact. LAB was unmounted. Secrecy analysis found
no exported private PSK value across the 135 retrieved files.

The native phase log shows EC/UCSI loaded but the battery auxiliary device
unbound. The explicit outer-init module list omits huawei_gaokun_battery, even
though that module is packaged. Candidate 131 adds this real module after EC
and a bounded read-only supply snapshot. It does not claim Battery HDI/UI
integration and must pass installation/boot admission separately.
