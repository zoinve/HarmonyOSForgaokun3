# Native QCA Bluetooth transport — trials 021 and 022

## Outcome

The original HarmonyOS Bluetooth startup timeout/abort boundary is repaired **within the bounded 022 native observation**. This is not a claim that both requested crashes, pairing, audio, suspend or long-term stability are fixed. A second independent crash remains unidentified.

018 preserved the actual Bluetooth SIGABRT report: HCI Reset `0x0c03` timed out, followed by the original abort timer. 019/020 failed honestly when the emulator `/dev/hwbt` transport was missing, but the original upper service still timed out and restarted. 021 proves real native controller operation; 022 connects that controller to the original service without changing its UID, identity, critical checks or abort logic.

## Reference application

- `right-0903/linux-gaokun` (GitHub; `linux-ego` redirects): board UART2, WCN6855, power sequence and firmware arrangement. The existing target kernel/device tree already contains the relevant wiring; neither was replaced.
- HarmonyMac: the already integrated real graphics and ashmem implementation remain unchanged.
- L410 HarmonyOS Adaptations: Bluetooth ABI and the concept of a privileged hardware broker serving an unprivileged original HDI process; also the existing scoped local-storage fallback. Its Hi1103-specific command translations and no-op power/LPM implementations were **not** copied into the QCA adapter.
- L410 Linux Compatibility Platform: original service/HDI dependency and FD handoff architecture; no replacement desktop or service identity introduced.

## Real hardware evidence

021 loads only the target kernel's existing `pwrseq_qcom_wcn` and `hci_uart` modules, with byte-verified firmware copied read-only from the working Ubuntu installation:

- `wcnhpbtfw21.tlv`: SHA256 `77d8979da5c613c85550549dcef8fb8ec6fe2e5576942855ea03179a11597c1f`.
- `wcnhpnv21g.bin`: SHA256 `1e2fd8954f88a8133b17a04c802f816fe1be2ca856fd60d620359f568c511fbf`.

Actual `HCI_CHANNEL_USER` binding and firmware setup succeeded. A real H4 Reset received `04 0e 04 01 03 0c 00`; no synthetic response was supplied. The probe closes its own descriptor afterward. 021's original service adapter was still the old fail-closed implementation, so hardware success alone was not treated as a service fix.

022 replaces only the RAM-bound vendor adapter with `native-qca-vendor-022.c` and adds a target-only root broker, `native-qca-broker-022.c`. The broker opens real `hci0` USER mode and converts packet framing to an unmodified H4 stream. It never rewrites commands, supported features, addresses, controller status or replies. The original `blue_host` remains UID 3021; the socket permits only that UID, and both endpoints check peer credentials. The original target's separate network namespace remains enabled. A bind-mounted pathname socket carries the stream into its vendor sandbox.

Power-on success requires successful real kernel controller setup. Initialization callback success requires that real channel. Closing the stream releases the actual HCI descriptor. Unsupported vendor LPM/wake operations return `ENOTSUP`, not fake success; their integration is still incomplete.

Actual 022 evidence:

- Root broker accepted original UID 3021 and successfully opened the real controller.
- Original HDI logged `TL_Startup success: 0` and `event_finish_startup`.
- 64 logged controller commands and 64 logged Command Complete replies, including successful Reset and subsequent initialization/scan configuration commands. Logging is bounded, not an exhaustive HCI trace.
- Controller opcode `0x0c6d` actually returned status `0x11`; this nonzero reply was preserved and handled by the original stack, not rewritten as success.
- Original `bluetooth_service` PID 466 remains the same at samples 3–11. No recorded Bluetooth timeout, abort or service restart; all 53 snapshots contain no SIGABRT/SIGSEGV exit line.
- Four fault-file capture passes (samples 2, 5, 8, 11) found no fault files. This is bounded evidence, not proof that no future failure is possible.
- Original unlocked-screen event was recorded. No new visual screenshot assertion is made in this review.

## Verification and preserved state

`verify-native-qca-runtime-021-022.py` validates all 55 + 53 raw snapshot SHA256 values, real replies, original service identities/domains, 12 target SELinux permissive samples per trial, read-only original images, namespace root, overlays, Ubuntu return and default boot. The early policy-load audit rolled out of the final ring; its absence remains explicitly reported, not fabricated.

The host-only disposable H4 test exercises packet boundaries, rejects invalid framing, proves a missing real broker cannot provide a channel or initialization callback, and checks honest unsupported-LPM failure. Both target executables still refuse non-PID1 operation; actual native refusal tests returned 77. Builds use warnings-as-errors. No host Bluetooth service, module, firmware, security or package was modified.

021 and 022 each booted exactly once and automatically returned to Ubuntu. Final 022 Ubuntu boot ID: `c5b67a9e-da97-4db0-9474-92bf67ec18c5`. Three original SDK image hashes and 81 static EFI files remain unchanged after 022; normal boot random-seed rotation is recorded separately. Persistent Ubuntu default, screen-off timer, host LSM and read-only LAB mount are preserved.

022 reclaimed only the proven-unreferenced EFI copy `native-original-graphics-012/initrd.img`, after comparing it with the retained original staging artifact. Its source image and numbered logs remain. Post-install ESP free space was 97,001,472 bytes. No unrelated boot entry was removed.

After verification, `clean-completed-native-boot-entries-003.py` removed only four spent entries 018–021, retaining every boot payload and evidence file. An initial dry run including 017 refused before any write: that entry now has suffix `+0-3` rather than the historical `+0-1`, showing subsequent reuse. Its contents/use were not discarded; cleanup was narrowed to 018–021, dry-run checked, then applied. All 80 other EFI files were unchanged. Final read-only SSH verification confirms both the reused 017 entry and current 022 entry remain, Ubuntu is still current/default, no one-shot remains, and the screen-off timer/host LSM are unchanged.

Final checks passed: nine candidate artifact hashes, the disposable H4/fail-closed test, all 108 raw snapshot hashes, 11 Python syntax checks, and rejection of a corrupted disposable evidence fixture. No completed operational trial was rerun for these checks. Results are recorded in `native-original-graphics-boot-022/final-verification.json` and `host-final-verification.json`.

The build inherits a historical `qca-bringup.json` field `transport_bridge_installed=false` from 021. That field describes the earlier probe, not 022's runtime; the separate `qca-bridge.json`, actual adapter source hashes and real runtime evidence describe 022. Original generated evidence is retained unchanged.

## Limits

Only the reproduced Bluetooth transport/startup crash has been addressed and verified in this window. Pairing, discovery results, ACL/audio traffic, LPM/wake, suspend and long-running behavior remain unverified. A second independent crash cannot truthfully be marked fixed without its own report and root cause. Completed trials and raw logs must not be overwritten or rerun.
