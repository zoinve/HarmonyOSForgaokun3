# Hardware integration 892

Both the RAM EGL bridge and unchanged product EGL/GLES frontend again passed a real VirGL (FD690) context and green-pixel readback. This does not establish full-system presentation or desktop success.

Per-process bridge traces were obtained only for standalone diagnostic children. Read-only filesystem inspection explains the blind spot: `/data/local/tmp` is owned by UID/GID 2000 with mode 0771, so absence of a RenderService file is not proof that it makes no EGL calls.

Fresh diagnostic payload 893 moves bounded traces to a new sticky RAM directory under `/dev`, with per-process files created using `O_NOFOLLOW`, mode 0600. Existing service identities and directory permissions are untouched. A root read-only observer reports these traces and up to 64 threads per selected process. Rendering behavior and the product frontend remain unchanged.

Payload 893 SHA-256: `c03e8b9534361cdff721fc4825405616cd3dbd17a8c7094437156c298753b9c3`. The actual archive executable-mode check passed. Experiment 892 was stopped gracefully; post-run integrity checks and userdata removal are recorded separately.
