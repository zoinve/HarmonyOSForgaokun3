"""Repeat loader unit guards against the distinct native 164 loader generator."""
from pathlib import Path

BASE=Path(__file__).resolve().parent


if __name__=='__main__':
    source=(BASE/'test-live-debug-loader-161.py').read_text().replace('build-commercial-native-161.py','build-commercial-native-164.py')
    source=source.replace("['loader161']","['loader164']")
    exec(compile(source,'test-live-debug-loader-164.generated.py','exec'),globals())
