# Headless 877: render stall during normal OOBE navigation

- Native ARM/KVM, 1920×1080, original read-only system disks and independent userdata; physical backlight remains off.
- Keyboard Tab/Enter genuinely advanced welcome → language → region. Enter on region was received: application logs report `show next page quick_setup` and `RegionSelect aboutToDisappear`.
- The displayed region transition remained unchanged after multiple minutes (`next-experiment/region-late-877.png`). This is not evidence of a lost mouse event.
- Native watchdog report identifies RenderService blocking in a vSync task. Its RSUniRender thread was running inside Mesa softpipe TGSI fragment-shader execution, including texture instruction handling. Two samples five seconds apart accumulated approximately five CPU seconds and showed different instruction paths. This does not establish an infinite loop.
- Symbolization used the original `lab-softpipe167/libgallium25.0.1.so`; `fetch_src_file_channel`, `exec_tex`, `exec_instruction`, `tgsi_exec_machine_run`, and `shade_quads` resolved from its symbols/debug information. No exported/native llvmpipe screen constructor was found in the full symbol search; only softpipe's constructor matched.
- After collecting the late screenshot, QMP `quit` ended the guest early for a single-variable resolution comparison. Runner still performs its normal post-run integrity checks; their completion is reported separately.
- Experiment 878 uses the same kernel/payload and a fresh userdata copy, with explicit diagnostic framebuffer 960×540. Default launcher resolution stays 1920×1080. No watchdog, shader, activation, account, trust, or readiness bypass is applied.

Desktop is **not verified**. A low-resolution comparison is diagnostic, not the final display fix.
