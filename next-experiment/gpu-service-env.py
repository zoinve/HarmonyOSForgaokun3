"""Prepare a RAM-only graphics configuration for the real VirGL driver."""
import copy


def virgl_service_config(original):
    result = copy.deepcopy(original)
    services = [s for s in result['services'] if s['name'] == 'render_service']
    assert len(services) == 1
    conflicts = {'LIBGL_ALWAYS_SOFTWARE', 'GALLIUM_DRIVER', 'MESA_LOADER_DRIVER_OVERRIDE'}
    services[0]['env'] = [e for e in services[0]['env'] if e['name'] not in conflicts]
    return result
