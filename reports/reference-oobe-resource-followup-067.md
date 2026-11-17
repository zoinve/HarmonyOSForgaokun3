# Reference StartupGuide Resource Handling

Local source reviewed: references/L410-HarmonyOS-Adaptations/oobe-resources/
oobe_rawfile_path_compat_v3.cpp and README.md, using the pinned reference tree.
No reference deployment or preload was executed.

L410 interposes the private C++ HapManager::FindRawFile symbol. Only in process
com.huawei.hmos.hwstartupguide, it strips an optional rawfile/ prefix, rejects
empty/absolute/dot/parent/empty-component names, then attempts to open the
original extracted resource under one of two compile-time roots:

- /data/storage/el1/bundle/pc_hwstartupguide/resources/rawfile/
- /data/app/el1/bundle/public/com.huawei.hmos.hwstartupguide/pc_hwstartupguide/resources/rawfile/

On an accessible candidate it returns the real path; otherwise it calls the
stock implementation through RTLD_NEXT. It does not complete provisioning.
This is an implementation description, not a security review or proof that its
private ABI and paths match this device. In particular, it explicitly refuses
empty names, so it does not directly fix the observed name-is-empty warning.
Successful original Lottie resource loads in 066 also mean that a universal
rawfile failure cannot be inferred from that warning.

HarmonyMac ports/tests/native-desktop-start.sh instead explicitly invokes
aa force-stop on hwstartupguide. That shortcut is not adopted: it would hide
the normal first-run workflow rather than establish that it works here.

The Linux Compatibility Platform provides the later AnCo/Wayland Linux-app
integration, not an alternate cure for original StartupGuide/SceneBoard
startup. The composer, namespace and EGL/queue/KMS references remain recorded
in reference-three-projects-001.md. None is evidence of a ready-made fix for
this device's BMS GetLauncherAbilityInfoSync wait or malformed input packages.

Operational 067 uses only bounded late graphics observation, not any of the
private resource interposition or StartupGuide force-stop methods above.
