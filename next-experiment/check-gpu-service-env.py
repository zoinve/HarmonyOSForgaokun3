"""Only remove the three conflicting software-driver overrides."""
import importlib.util
import json
from pathlib import Path

base = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('service_env', base / 'gpu-service-env.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original = json.loads((base / 'gpu-runtime-883/original-graphic.cfg').read_text())
expected = json.loads(json.dumps(original))
service = next(s for s in expected['services'] if s['name'] == 'render_service')
removed = {'LIBGL_ALWAYS_SOFTWARE', 'GALLIUM_DRIVER', 'MESA_LOADER_DRIVER_OVERRIDE'}
service['env'] = [e for e in service['env'] if e['name'] not in removed]
actual = module.virgl_service_config(original)
assert actual == expected, 'No changes to service identities, permissions, jobs or other environment'
assert original != actual, 'Original input must remain unchanged'
assert module.virgl_service_config(actual) == actual
print('PASS: only software-driver constraints removed; original configuration preserved')
