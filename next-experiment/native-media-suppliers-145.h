#ifndef NATIVE_MEDIA_SUPPLIERS_145_H
#define NATIVE_MEDIA_SUPPLIERS_145_H

static const char *const native_media145_modules[] = {
    "lpasscc_sc8280xp", "pinctrl_sc8280xp_lpass_lpi"
};

static void native_media145_load(void)
{
    double start = native_media136_now();
    dprintf(1, "MEDIA145_SUPPLIERS_BEGIN group_seconds=12 per_probe_seconds=4\n");
    for (size_t i = 0; i < sizeof(native_media145_modules) / sizeof(native_media145_modules[0]); ++i) {
        const char *module = native_media145_modules[i];
        double now = native_media136_now();
        if (!isfinite(start) || !isfinite(now) || start < 0 || now < start || now - start > 8) {
            dprintf(1, "MEDIA145_SUPPLIERS_STOP module=%s reason=group_budget_or_clock no_retry=1\n", module);
            break;
        }
        char path[256];
        snprintf(path, sizeof(path), "/sys/module/%s", module);
        if (!access(path, F_OK)) {
            dprintf(1, "MEDIA145_SUPPLIER_PRESENT module=%s binding_not_inferred=1\n", module);
            continue;
        }
        char *args[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", (char *)module, NULL};
        int result = probe(module, args, 4);
        dprintf(1, "MEDIA145_SUPPLIER_RESULT module=%s status=%d binding_not_inferred=1\n", module, result);
        if (result == 124 || result == 125) {
            dprintf(1, "MEDIA145_SUPPLIERS_STOP module=%s reason=probe_timeout_or_refusal no_retry=1\n", module);
            break;
        }
    }
    dprintf(1, "MEDIA145_SUPPLIERS_END hardware_success_not_inferred=1\n");
}

#endif
