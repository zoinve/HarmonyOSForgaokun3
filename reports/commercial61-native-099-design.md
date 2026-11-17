# Native 099: Reference Service-First Ordering

User clarification: the supplied image is the reference image. Do not download
another image or treat a different base image as a demonstrated cause. The
remaining unproven parity is runtime adaptation/configuration, not a request
for another original image.

This candidate tests one concrete untried difference on the working early
physical-identity stack: start the exact HarmonyMac script as the existing
diagnostic init service begins. Its SA probe precedes SceneBoard start, which
precedes its first guide PID query. Prior 077/078 waited for both existing
SceneBoard and guide before sending the SceneBoard start; 078 added a Dock
gate. Neither is an exact ordering reproduction. 095 tested only Alt+F4.
097 proves the local relaunch callback, but does not prove that startup order
can or cannot affect the state in which the first stop is delivered. This is
a single parity experiment, not a proposal to repeat arbitrary stop delays.

The reference is read from Git at pinned commit
f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad and checked against the local checkout
allowing only Windows checkout CRLF conversion. Executable LF source SHA256:
fa45837b06d1ce1543be51d3b8f710c3a99213faa9e176dbc01a7de0fcd60334.
The sole content change is redirecting the log to an already exported own
diagnostic filename. Source command order, SA set, 120/180 polling limits,
ten-second sleep and single original aa force-stop remain identical. Do not
interpret the source's unconditional NATIVE_DESKTOP_READY marker as success.
The tests explicitly preserve its proceed-after-timeout and command-failure
behavior instead of silently substituting a stricter, different script.

099 disables the launched 095 Alt+F4 worker but retains its unused artifacts
unchanged in the archive. A separate observer runs the reference once, then
records process IDs and original WMS dumps at uptime 90/110/130/145. These are
read-only observations, not another kill or an altered lifecycle callback.
095's original hardware digest/privacy and real WPA diagnostics remain intact;
the WPA cycle can refuse its guide-presence gate if the guide stays stopped.
That refusal is evidence, not permission to force a network status.

The new delta is exactly three RAM archive members, 2,417 bytes compressed,
SHA256 45cb1d357e540026f8aafd3c397dd993d56af7c22bfa3c73ff4845f5cf4f6382.
Ordered overlay merging is equal to the new full archive. Original init/service
permissions, SceneBoard/guide packages, callbacks, provisioning, authentication,
images, core binaries, 120/140-second full-frame captures and 132-second real
keyboard observation remain unchanged. Seven shell-control scenarios pass.

Install and run require inherited original-image/EFI hashes, Ubuntu current and
default, strict trusted host key, active/enabled screen-off timer, memory/free
space admission, immutable numbered evidence, one bounded boot and archived
two-entry retention. Desktop acceptance still requires stable original desktop
pixels and an independently correlated visible interaction; PID absence and
command success alone are insufficient. Never rerun this numbered boot.
