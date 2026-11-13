"""Fresh isolated TCG queue trial; preserve every numbered result."""
from pathlib import Path
import runpy


def launcher_source():
    source = runpy.run_path(str(Path(__file__).with_name('run-composer-fd-001.py')), run_name='offline_generator')['launcher_source']()
    for old, new in [('composer-fd-run-001', 'composer-queue-run-001'),
                     ('composer-fd-package-001', 'composer-queue-package-001'),
                     ('composer-fd-runtime-001', 'composer-queue-runtime-001'),
                     ('composer-fd-runner-001', 'composer-queue-runner-001'),
                     ('build-composer-fd-001.py', 'build-composer-queue-001.py'),
                     ('FD001_CASE ', 'QUEUE001_CASE '), ('FD001_PASS ', 'QUEUE001_PASS ')]:
        assert old in source, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__ + ':generated', 'exec'))
