# Native Audio Dependency Diagnosis 141

The single bounded 141 boot returned to Ubuntu with boot ID
`3b78224e-744b-4b90-9131-09dbdd836f2b`. Retrieved run
`commercial61-native-087-51f234c0-4c71-4f9f-960c-250670df9041` contains 175
files; every exported file hash matched. Original images and firmware,
Ubuntu current/default entry and enabled/active screen-off timer passed return
verification. LAB was unmounted. Experimental entry 136 was archived before
its authorized removal; shared payloads remain intact.

## Actual Findings

- Early debugfs mount succeeded. Deferred-probe samples are now readable and
  complete (`eof=1`, `errno=0`), unlike 139's failed ENOENT reads.
- Four audio macros wait for LPASS pinctrl suppliers under
  `/soc@0/pinctrl@33c0000`: `dmic23-default-state`, `rx-swr-default-state`,
  `tx-swr-default-state`, and `wsa-swr-default-state`.
- SoundWire controllers wait for the dependent RX/TX/WSA macros.
- The sound card initially reports a missing CPU DAI; later its reason becomes
  `WCD Playback: codec dai not found`.
- Thus ALSA cards and PCM devices remain absent. Supplying the board topology
  at the new kernel filename was not sufficient to register the card.
- Native original powermgr has 36 records matching real capacity/presence/current
  readings; real backlight readback correlation remains present.
- hci0 remains enumerated, but initialization/pairing is not accepted.
- Separate `qcom-cpufreq-hw: Failed to find icc paths` remains in the deferred
  list. Do not hide it or claim suspend/power integration complete.

## Next Change

145 explicitly loads the exact packaged `lpasscc_sc8280xp` and
`pinctrl_sc8280xp_lpass_lpi` modules. The latter's real modinfo dependency is
`pinctrl-lpass-lpi`; modprobe resolves it. Audit 144 verifies the module bytes,
aliases and ABI against the unchanged payload and Ubuntu enumeration.
Two four-second probes have a twelve-second admission budget and no timeout
retry. No mixer, amplifier, firmware binary, service identity or original-image
changes are made.

Evidence: `commercial61-native-141/binding-runtime-analysis-142.json`,
`commercial61-native-141/driver-runtime-analysis-142.json`,
`audio-suppliers-144/result.json`, original retrieval manifest and return audit.
Extra diagnostic unit tests cover existing debugfs, successful mount, mkdir
failure, mount failure, clock refusal, rate limiting, and source edit boundaries.
Overall basic-driver integration remains active and incomplete.
