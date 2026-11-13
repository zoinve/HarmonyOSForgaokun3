"""Independent read-only package/log/preservation checks for FD words/vectors."""
from pathlib import Path
import runpy


def launcher_source():
    source = runpy.run_path(str(Path(__file__).with_name('verify-composer-fd-001.py')), run_name='offline_generator')['launcher_source']()
    for old, new in [('composer-fd-001-independent-verification', 'composer-fdstream-001-independent-verification'),
                     ('composer-fd-package-001', 'composer-fdstream-package-001'),
                     ('composer-fd-run-001', 'composer-fdstream-run-001'),
                     ('composer-fd-runtime-001', 'composer-fdstream-runtime-001'),
                     ('FD001_CASE ', 'FDSTREAM001_CASE '), ('FD001_PASS ', 'FDSTREAM001_PASS '),
                     ('fd_ownership_only=True', 'fd_word_vector_only=True')]:
        assert old in source, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__ + ':generated', 'exec'))
