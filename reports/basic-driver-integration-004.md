# Basic Driver Integration 004

Date: 2026-11-16. Active objective: basic hardware integration on the
user-confirmed desktop, not further OOBE/activation work.

## Acceptance State

| Area | Evidence | Still Unverified |
| --- | --- | --- |
| Input | Original SceneBoard receives injected keyboard events; user confirms desktop | Physical touch, touchpad and full keyboard interaction |
| Display | Original RenderService/composer output; real backlight request/readback correlation retained in 136/139 | Slider interaction and physical luminance |
| Wi-Fi | Genuine supplicant/guest DHCP evidence from prior baseline | Full native NetManager and UI acceptance |
| Bluetooth | Packaged modules load; native guest exposes hci0 | Controller initialization, native stack, scanning and pairing |
| Audio | All 18 selected module probes succeed; SLPI/ADSP/CDSP reach running | ALSA card/PCM absent in 136/139; playback/capture and native HDI not accepted |
| Battery | Real EC readings reach original powermgr; 139 has 40 matching records | UI, plug/unplug transition, optional absent measurements |
| Power | Existing desktop baseline and Ubuntu screen-off preserved | HarmonyOS suspend/resume and charging transitions |
| USB | Earlier enumeration/backend evidence only | Native service and user-workflow acceptance |

## Audio Findings

Exact payload inspection 140 finds only
`lib/firmware/qcom/sc8280xp/HUAWEI/gaokun3/audioreach-tplg.bin`.
The exact packaged q6APM module uses `qcom/%s/%s-tplg.bin`; the current
machine driver and boot DTB select `sc8280xp` / `SC8280XP-HUAWEI-GAOKUN3`.
Candidate 141 supplies identical board topology bytes at the requested path.
This offline mismatch is not yet proof of the sole cause of missing audio.

139's diagnostic bus paths `/sys/bus/apr` and `/sys/bus/gpr` were wrong: the
kernel uses `aprbus`. Its deferred-probe reads returned ENOENT because the
outer diagnostic debugfs mount happened after the sampling window. Candidate
141 corrects these diagnostic limitations. Do not interpret those empty/failed
reads as an empty deferred-probe list or absent DSP services.

Exact-image audit 143 confirms the existing disabled L410 helper assumes a
Kylin glibc sysroot, CS35L36/TAS2562 SmartPA probing/bootstrap, and fixed mixer
control numbers. These are not valid WSA883x/WCD938x board initialization.
Do not simply enable that helper or reuse its amplifier routines.

## Reference Guidance

- L410-HarmonyOS-Adaptations: reusable VDI/ALSA IPC shape, but do not adopt
  failed-write-as-success fallback or L410-specific hardware setup.
- L410-Linux-Compatibility-Platform: Linux compatibility layer context, not
  evidence of this board's native service acceptance.
- HarmonyMac `ed213a08817c642e9b455fb7d8f5271da41631eb`:
  `ports/tools/enable-local-audio-host.py` enables original HDI only in its
  explicitly guarded virtual root and labels ALSA/hardware unqualified. Its
  host-index/config assumptions must not be copied onto this commercial image.

## Preservation And Evidence

136: 175 retrieved files, all hashes matched. 139: 178 files, all matched.
Both returned to Ubuntu with original images/firmware/default boot unchanged,
LAB unmounted and screen-off enabled/active. Old experimental entry files were
archived before removal; shared payloads were not removed.

See `commercial61-native-136-closure.md`, `audio-topology-140/result.json`,
`audio-helper-143/result.json`, and per-run `binding-runtime-analysis-142.json`.
141 is a candidate until its original runtime evidence has been retrieved and
analyzed. The overall basic-driver goal remains active and incomplete.
