"""Fresh no-device TCG FD trial, preserving both historical parser trials."""
from pathlib import Path


def launcher_source():
    source = Path(__file__).with_name('run-composer-parser-001.py').read_text()
    for old, new in [('composer-parser-run-001', 'composer-fd-run-001'),
                     ('composer-parser-package-001', 'composer-fd-package-001'),
                     ('composer-parser-runtime-001', 'composer-fd-runtime-001'),
                     ('composer-parser-runner-001', 'composer-fd-runner-001'),
                     ('build-composer-parser-001.py', 'build-composer-fd-001.py'),
                     ('PARSER001_CASE ', 'FD001_CASE '),
                     ('PARSER001_PASS cases=8 original_code=1 factory_called=0 payload_not_parsed=1 smq_not_tested=1 desktop_not_tested=1',
                      'FD001_PASS cases=8 original_code=1 factory_called=0 smq_not_tested=1 desktop_not_tested=1')]:
        assert old in source, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__ + ':generated', 'exec'))
