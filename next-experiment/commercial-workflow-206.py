"""Use206 only;205 was admitted locally but never installed or booted."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
source=(BASE/'commercial-workflow-205.py').read_text().replace('205','206')
exec(compile(source,str(__file__),'exec'),globals())
