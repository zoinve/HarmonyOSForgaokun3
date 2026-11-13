# 880: input received, software rendering stalls again

- Host recovered its existing EL2 kernel through the approved one-time boot entry. `/dev/kvm` and QMP KVM-enabled/present checks succeeded. The default boot entry was not changed. Physical backlight remained at zero.
- Native ARM/KVM, independent userdata, diagnostic 960×540 framebuffer. Normal keyboard navigation reached quick setup. Selecting Skip was recorded by the application, which logically advanced to `basic_service_statement`; the framebuffer stayed on quick setup. `agreement.png` is therefore not evidence of the agreement page.
- RenderService watchdog events at 08:51:49 and 08:51:54 show its render worker running inside Mesa softpipe/TGSI. Its CPU time increased by approximately five seconds across those five seconds. This is evidence of expensive/busy rendering, not proof of an infinite loop or a mutex deadlock.
- No agreement was accepted in this run. The user has authorized ordinary initialization agreements for subsequent normal navigation. No activation, account, trust or readiness database was edited.
- Original render-service binary contains `persist.sys.graphic.blurEnabled`, matching the documented visual-effect switch. Fresh payload 881 changes only the RAM init command list to set this cosmetic property to zero after persistent parameters load. It does not skip drawing, replace shaders or disable watchdogs. This is a hypothesis test, not a claimed repair.
- Payload 881 SHA-256: `b9eb297c9bb0cad8b4bc779b59d5b2bb8cba9c31fb93ee32062bc8379cdda1c6`.
- A final screenshot was saved remotely before requesting normal QMP quit. Post-run integrity checks and stopped-userdata cleanup are recorded separately after completion.

No genuine desktop has been verified.
