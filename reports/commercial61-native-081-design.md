# Original MHI/QRTR transport 081

Goal remains a real original HarmonyOS desktop with full-resolution pixels and
genuine visible interaction. Physical Wi-Fi and original NetManager admission
are prerequisites, not substitute success conditions.

080 recovered genuine Wi-Fi PCI enumeration, WCN6855 hw2.1 identity and MHI
power-on success after original power modules were loaded. No PHY appeared in
its complete ten-second early window. Its final dmesg was budget-refused.
Read-only local kernel sources link ath11k's IPCR MHI channels to the qrtr_mhi
driver and original QMI capability request/firmware version reporting. The
original transport module is packaged but was absent from 080's module list;
the working Ubuntu list includes it. This is the next grounded dependency.

Exact candidate delta from 080: outer init only. Load original qrtr_mhi with
an eight-second command bound before ath11k_pci, preserving existing power
order, original firmware, original service definitions and bootstrap. Keep the
ten-second early PHY observation and add MHI device/driver/modalias inventory.
No kernel instruction, device ID, original QMI handler or activation check is
modified. No scan, association, Wi-Fi credential read or OOBE stop is requested.

Add an independent read-only /dev/kmsg cursor opened O_NONBLOCK|O_CLOEXEC.
Sample before original target handoff and on existing periodic diagnostics.
Limit each call to 512 records / approximately 128 KiB (at most one 8192-byte
record beyond the byte threshold), and at most five consecutive overrun reads.
Preserve selected original ath11k/MHI/QRTR/firmware records and report errors,
overruns and incomplete coverage. Reading this cursor does not clear global
kernel logs. Also read at most 32 outer netif/PHY links each periodic call.
No new background helper, watchdog changes or unlimited drain is introduced.

Reader tests compile the exact C function with mocked open/read; actual host
kmsg is never read by unit tests. Test read-only flags, original record text,
EAGAIN, bounded EPIPE retry, record/byte caps, open failure, cursor reuse and
unexpected read failure. Admission additionally requires exact init-only delta,
packaged transport, bounded ordered probes and preserved CLONE_NEWNET.

Keep original 270-second outer and 150-second target limits, Ubuntu default,
enabled/active screen-off timer, original images/manual entry and 32 MiB ESP
headroom guard. Hash-archive/remove only entry 079 after installing 081; keep
080/081 entry files and every shared payload. Execute one numbered 081 boot,
recover evidence read-only, and verify preservation after return.

Real outer PHY/firmware identity will not prove target networking: no namespace
transfer or supplicant/NetManager bridge is attempted here. Kernel log absence
must not be treated as absence throughout runtime if reads fail or overrun.
OOBE completion and visible interactive desktop remain mandatory later gates.
