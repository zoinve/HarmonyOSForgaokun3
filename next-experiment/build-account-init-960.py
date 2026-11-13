"""Fresh initrd with descriptor-based root discovery; preserve completed 959."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'build-account-init-959.py').read_text().replace('959','960')
exec(compile(source,'build-account-init-960-generated','exec'))
