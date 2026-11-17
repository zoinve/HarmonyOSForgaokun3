# Candidate 158: root fix tested, operational boot withheld

158 was built, passed eleven focused/baseline test scripts and a byte-identical
helper rebuild, and was installed without changing the persistent Ubuntu default.
The new root-resolution regression test reproduces the absolute `/system` link:
ordinary external `openat` fails, while root-anchored `openat2` succeeds and
does not permit access to paths outside the fixture root.

No 158 boot was requested and no native runtime acceptance is claimed.

Before boot, the actual retrieved 157 evidence was checked again. Its latest
phase log records `192.168.10.142` on wlan0 at lines 90279, 151502, 215447 and
281910, whereas the earlier 153 run had `192.168.10.210`. The fixed-address
sidecar gate and client inherited from 157 are therefore not reliable for
a new DHCP lease. Booting 158 unchanged would not be a justified validation.

158's root fix remains valid offline evidence; dynamic native address selection,
diagnostic-only config generation and client discovery must be completed before
the next operational candidate. Discovery must not substitute for pinned SSH
authentication, scan unrelated hosts, change host firewall/routing settings,
retain a wildcard SSH binding, or export credentials.

`live-debug-address-159.h` and its focused test implement the first part:
select exactly one current wlan0 IPv4 address in the observed lab subnet,
reject absent/ambiguous/invalid addresses, and replace only the dedicated RAM
diagnostic config's listen line, with exclusive creation and no host-config edit.
This helper is not yet integrated into a native candidate and is not runtime proof.

158 installation checked prior EFI files/default/firmware and retained the
original manual entry. The subsequent authorized retention archived/removes
only the old 153 entry, keeping 157/158. No shared payload was removed.
Current Ubuntu boot ID remains `11ebd438-9365-46fe-a5ae-e243b6fcae5e` from the
verified 157 return. The all-basic-driver goal remains incomplete and active.
