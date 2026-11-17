"""Read-only evidence retrieval with no journal replay on the original partition."""
from pathlib import Path
source=Path(__file__).with_name('retrieve-commercial-evidence-001.py').read_text().replace('commercial61-native-001','commercial61-native-004').replace('commercial-return-audit-001','commercial-return-audit-004')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
