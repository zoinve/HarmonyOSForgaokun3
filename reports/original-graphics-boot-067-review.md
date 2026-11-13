# Original graph 067 — extended observation

The isolated virtual-display guest ran for its 360-second observation bound.
Original RenderService PID684 remained observed with UID1003 and its original
SELinux domain. Original composer PID909 and allocator PID879 retained their
original identities. All 48 observed SELinux samples were permissive.

Actual RenderService calls created EGL contexts and successfully made them
current through the software Mesa bridge. Both replacement VDIs were observed
mapped. No Foundation critical fault or guest reboot appeared within the bound.
This does **not** establish a working screen or desktop.

Original decoded RenderService logs explicitly report:

> RSScreenManager: SetScreenBacklight: There is no screen for id 0

The earlier RenderService ready-parameter write is not evidence of successful
screen enumeration. Both original hidumper screen queries exited3. The next
diagnostic (068) adds bounded original HiLog queries for the actually discovered
composer and HDF-manager PIDs; providers, kernel and service configurations stay
unchanged. Its outcome is not assumed here.

`original-graphics-boot-067-independent.json` independently checks the serial,
all 12 injected libraries, initrd, kernel, three complete original SDK images
and 378 prior native raw files. No host SSH, boot, security or screen-off setting
was changed. All runtime evidence is from an isolated WSL software VM, not the
physical MateBook display.
