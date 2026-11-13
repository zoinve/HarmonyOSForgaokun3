# 033 — unattended cursor validation and automatic return

User request: enable automatic exit from HarmonyOS, continue cursor adaptation and then rendering acceleration without waiting for further milestone approval.

033 retains the 032 cursor implementation and 031 Binder kernel. A last, 309,217-byte gzip/newc initramfs replaces **only `/init`**. The base 032 initramfs, original kernel/DTB, original images, 030/031/032 entries and Ubuntu default are unchanged. All 96 existing EFI files passed hash comparison after installation. EFI free space is 40,685,568 bytes; nothing was deleted.

The parent samples the target for approximately 240 seconds, terminates the target namespace, snapshots evidence and normally unmounts the lab filesystem before reboot. A separate process, armed before storage/module I/O, attempts reboot at 420 seconds even if the parent blocks. This last-resort path deliberately avoids a potentially blocked sync. It is **not a hardware watchdog** and cannot guarantee recovery from a wedged kernel. The entry uses `panic=15`; manual entries keep their original settings.

The 033 archive builder originally emitted inherited 032 manual-mode metadata. Its historical `result.json` is retained unchanged. The authoritative `return-overlay-result.json` explicitly supersedes those three fields: 420-second outer fallback, 240-second target budget and manual-only operation false. The separately rebuilt unused volatile scratch filesystem is not installed; 032's empty scratch image is reused. Archive comparison checks all other members are byte-identical, including the target bootstrap and graphics binaries.

Source deadline checks passed, both real native non-PID1 guards refused execution (exit 77), and the overlay's only-member reconstruction/hash check passed. These are not proof of automatic return or functional physical input. `boot-attempt.json` and `boot-observation.json` record the single new operational attempt; never rerun it under this number.

No artificial input is injected. An unattended boot cannot prove that physical clicks, touchpad movement or cursor visibility work for the user. Statusbar geometry remains unchanged pending actual visual evidence. Rendering acceleration work first targets the known CPU landscape-rotation stage; neither successful compilation nor an isolated benchmark proves desktop 120 FPS.
