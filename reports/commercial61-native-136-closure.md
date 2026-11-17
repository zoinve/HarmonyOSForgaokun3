# Native Basic Drivers: Run 136

## Scope

Continue the user-confirmed desktop baseline. No OOBE/activation change.
Explicitly load the packaged board audio/Bluetooth modules, then observe real
kernel resources without modifying mixers, amplifiers or native service credentials.

## Results

- The single bounded boot returned to Ubuntu. Boot ID changed to
  `db4fbb4c-2460-474e-abed-fa0da956d6cd`.
- Retrieved run `commercial61-native-087-1663b765-9ed9-40e7-9783-bb212473a545`:
  all 175 exported file hashes matched.
- All 18 requested module probes returned zero. This is module-load evidence,
  not device-binding or functional acceptance.
- SLPI, ADSP and CDSP initially reported offline, then reported running in the
  later native-service samples.
- `hci0` exists. Controller firmware initialization, native stack operation,
  scanning and pairing are not verified.
- ALSA card and PCM lists remain empty throughout the recorded samples. Only
  the ALSA timer node was observed. Native playback/capture are not verified.
- Real battery sysfs readings and matching original powermgr records remain
  present: capacity 98, present 1, current 0. One observed powermgr voltage is
  8298000 microvolts. The inherited analyzer's stronger path-log predicate is
  false because its expected path-discovery log is absent from this capture;
  do not silently interpret that predicate as either regression or full acceptance.
- Original-service backlight requests still correlate with real hardware
  readback. Physical luminance and UI slider interaction remain unverified.
- Temperature and health remain unavailable as hardware measurements.

## Preservation

Return verification passed: Ubuntu current/default, original manual entry retained,
screen-off timer enabled/active, firmware and all four original images unchanged,
LAB unmounted, and 169 prior EFI files unchanged except the boot-managed random
seed. The archived removal of experimental entry 131 is user-authorized.

## Next Diagnostic

Run 139 adds bounded read-only delayed-probe and audio-bus binding observations.
Resolve the missing ALSA card before adapting native audio transport. No claims
of audible playback, capture, Bluetooth pairing, suspend/resume or completion of
the overall basic-driver goal are made.

Evidence: `commercial61-native-136/media-runtime-analysis-138.json`,
`commercial61-native-136/driver-runtime-analysis-138.json`, original retrieved
manifest and preserved boot/return audit records. Parser tests: 3 passed.
