# Radio follow-up 272

Date: 2026-11-17, Asia/Shanghai.

The user requested autonomous testing while asleep. Current priority remains
Bluetooth enablement, nearby Wi-Fi discovery, and correct public device details.
Settings access is user-confirmed. USB work remains paused and preserved.

## Boot262

- Booted once, returned to Ubuntu without an additional reboot request.
- Return observed at 2026-11-16T16:53:03.673805+00:00; cause not inferred.
- Read-only retrieval265 recovered two phase snapshots, no user-space logs.
- phase-107.log contains PERSISTENT166_REFUSED identity_or_lock errno=17,
  followed by NATIVE_ORIGINAL_REFUSED loop_setup. Wireless changes were not run.
- errno17 is not proof of an actual lock conflict: the combined predicate does
  not set errno for every metadata/UUID mismatch.
- Build261/262 compiled init.c in a temporary directory without the customized
  persistent-data-166.h. Include search selected the generic BASE header before
  parent253. This mismatched the old165 path and Settings197 UUID.
- No disk validation suite, replay or offline data mutation was requested.

## Candidate266

- Uses the same radio logic as262 and inherits253's four customized headers
  into the compilation directory. Identity checks and exclusive locking remain.
- Compiled with warnings-as-errors and installed through267.
- Retains desktop173, Ubuntu default and screen-off timer; retires262 entry
  with archived contents. Shared payloads and original images remain.
- Started once. Read-only native endpoint authenticated at
  2026-11-16T16:57:12.138262+00:00 using pinned host key.
- Endpoint reported hilog and native logs available. This is not radio/UI
  acceptance. See commercial61-native-266/radio-live-observation-268.json.
- Collection269 excludes235,253,262 and all previously excluded runs.
- Bounded observer271 never requests reboots on connectivity timeout.

## Static follow-up

- Image Wi-Fi profile uses libl410_wifi_compat_v20.z.so. Reference README maps
  v20 artifact to source entry v18, which includes the shared v2 implementation.
- The reference sends SCAN_RESULTS to supplicant and serializes scan entries
  into Ashmem. Callback failure29189 alone does not establish an ABI mismatch.
- Deviceinfoservice strings inspection270 found no matching name-setting
  contract; do not infer a supported write API or edit SQLite blindly.
- Public defaults are in candidate266. Persisted device-name migration and UI
  verification remain pending. Preserve physical serials and original UDID.

## Next

Await this266 boot's return, retrieve269, inspect original HDF binding, blue_host
registration, real QCA command/completion evidence, and RADIO261_SCAN_RESULTS
counts. Do not install or reboot266 a second time. Never claim UI acceptance
based only on kernel enumeration, service startup or a read-only debug connection.
