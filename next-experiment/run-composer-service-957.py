"""One original-service ABI test; no desktop success inferred."""
from pathlib import Path

base=Path(__file__).resolve().parent
source=(base/'run-composer-kms-952.py').read_text()
source=source.replace('official-composer-kms-952','official-composer-service-957').replace('composer-kms-runtime-952','composer-service-runtime-957')
source=source.replace("result['probe_pass']='COMPOSER_FULL_PROBE_PASS' in text", "result['probe_pass']='ORIGINAL_COMPOSER_SERVICE_PASS' in text")
exec(compile(source,'composer-service-957','exec'))
