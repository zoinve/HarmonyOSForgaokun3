# 913: real 1080p navigation, observation timeout

The framebuffer observer saved actual 1920×1080 welcome, language, region and quick-setup pages. QMP keyboard navigation worked. These are OOBE pages, not a desktop.

The run ended early because a scheduled QMP screendump timed out waiting for QMP capabilities; the runner's finally block terminated QEMU. This was not a demonstrated guest GPU crash. Local and remote integrity results confirmed all original disks and protected userdata unchanged; only the stopped independent userdata was removed after verification.

For fresh 914, only the host observation behavior changes: VirGL configurations disable scheduled QMP screenshots, which have never exposed this framebuffer display. The guest's bounded read-only framebuffer observer remains the image source. Other QMP operations, native KVM and disk protections remain required. Ten active configuration/observer checks passed, including an actual runner capture-block test proving disabled capture does not invoke QMP.

914 reuses the immutable 913 payload; rendering libraries and service configurations are unchanged. No genuine desktop has been verified.
