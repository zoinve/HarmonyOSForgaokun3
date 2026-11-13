# 885: product EGL loading diagnosis

RenderService mappings confirm that it loaded the new Mesa EGL, VirGL Gallium, GBM, SDK C++ runtime, and RAM-bound NativeWindow bridge alongside the unchanged product EGL/GLES frontends and platform C++ runtime.

Both independent EGL display-initialization probes failed. Their output identifies the missing backend: `/system/lib64/lab-virgl883/gbm/dri_gbm.so`. The payload copied only top-level shared libraries, omitting the installed `gbm` subdirectory; the library also retained its build-time backend search path. See `next-experiment/diagnostic-885.txt`. No full-system frame or desktop has been verified.

Prepared fresh payload 886 includes the built `gbm/dri_gbm.so` and supplies `GBM_BACKENDS_PATH=/system/lib64/lab-softpipe-167/gbm` to product init and the independent EGL probes. The existing frontend, drawing implementation, service protections, and original images remain unchanged. Native ARM static compilation and the search-path regression test passed. SHA-256: `6c136196de6039398d32b4925cfbeed8d46dda4ad05a51002cb8f51a24512013`.

A graceful QMP quit was requested for 885. Its final integrity checks must pass before deleting its experimental userdata and starting 886.
