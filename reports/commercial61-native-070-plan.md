# Native 070: Stock Preinstall Rawfile Layout

Hypothesis, not proven runtime path: Ace logs use HAP resource loading and
stock FindRawFile derives a resources directory adjacent to its index path.
069 found the original HAP but no adjacent extracted resources. Original HAP
ZIP contains all three videos named in the failing rawfile requests.

070 adds exactly 46 original resources/rawfile files (6402165 bytes) to the
existing RAM upper layer at /system/app/HwStartupGuide/resources/rawfile.
The final /system overlay remains read-only. Original HAP, images, service
binaries, EGL, composer, application identity, installed records, sandbox
configuration and provisioning state are unchanged from 069. Only init and
bootstrap among existing archive members differ. Resources are mode 0444.

No module is fabricated under the BMS public install tree. No reference
private FindRawFile interposition or StartupGuide force-stop is used.
Generated resource layout is created before the original init/services run.
All additions are discarded with the diagnostic RAM filesystem.

Preserved full-frame 068 capture and 069 path inventory will distinguish a
stock-path repair from an ineffective adjacent directory. Success requires
original resource calls and actual pixels, not root-readable files alone.
Desktop and normal interaction remain separate, unproven goal requirements.

Admission: original HAP SHA256 and every ZIP CRC checked; traversal, malformed
components, symlink and unsafe-name fixtures rejected; exact archive additions
and unchanged remaining members verified. Native wrappers cross-compiled;
PID/root guards passed on installation. Full ordered overlay equals full image.
