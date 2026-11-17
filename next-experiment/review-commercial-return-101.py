"""Preserve full-frame OCR/differences and verify actual native identity evidence."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE/'review-commercial-return-095.py').read_text().replace('commercial61-native-095', 'commercial61-native-101')
source = source.replace('original_udid_success_proven_by_separate_native_helper=True',
    "original_udid_success_proven_by_separate_native_helper=bool(re.search(rb'HARDWARE091_GETDEVUDID phase=before[^\\n]*return=0[^\\n]*length=64[^\\n]*valid_hex64=1', read('snapshot075-commercial-desktop086.log')))")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
