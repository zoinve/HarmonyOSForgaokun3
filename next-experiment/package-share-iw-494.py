"""Reuse verified read-only iw capture; package locally without host changes."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


if __name__ == '__main__':
    stage = Path('/home/zoinve/harmony-virgl-883/native-iw-082')
    package = stage.with_name('share-iw-package-494')
    report = ROOT / 'reports/share-tools-494'
    assert not report.exists() and not package.exists()
    report.mkdir()
    source = (ROOT / 'next-experiment/package-native-wpa-083.py').read_text()
    # Preserve the established member, architecture-capture and digest checks.
    source = source.replace("'reports/commercial-network-inputs-audit-083/package.json'",
                            "'reports/share-tools-494/package.json'")
    source = source.replace('network083/', 'share494/')
    source = source.replace("('.', 'network083')", "('.', 'share494')")
    source = source.replace('native-wpa-tools-083', 'share-iw-tools-494')
    namespace = dict(__file__=str(ROOT / 'next-experiment/package-native-wpa-083.py'),
                     __name__='share_iw_package')
    exec(compile(source, namespace['__file__'], 'exec'), namespace)
    namespace.update(STAGE=stage, PACKAGE=package)
    namespace['main']()
