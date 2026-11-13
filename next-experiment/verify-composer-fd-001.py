"""Read-only independent FD evidence/package/host verification."""
from pathlib import Path


def launcher_source():
    source = Path(__file__).with_name('verify-composer-parser-002.py').read_text()
    for old, new in [('composer-parser-002-independent-verification', 'composer-fd-001-independent-verification'),
                     ('composer-parser-package-001', 'composer-fd-package-001'),
                     ('composer-parser-run-002', 'composer-fd-run-001'),
                     ('composer-parser-runtime-002', 'composer-fd-runtime-001'),
                     ('PARSER001_CASE ', 'FD001_CASE '), ('PARSER001_PASS cases=8 ', 'FD001_PASS cases=8 '),
                     ('parser_only=True', 'fd_ownership_only=True')]:
        assert old in source, old
        source = source.replace(old, new)
    marker = "    prior = json.loads((BASE / 'reports/composer-smq-001/result.json').read_text())"
    assert source.count(marker) == 1
    source = source.replace(marker, "    assert hashlib.sha256(after['system/lib64/lab-softpipe-167/libhdifd_parcelable.z.so'][1]).hexdigest() == '9b7635a5e1ada2ad682c4c36cc7c07b631938673714fbfa03256c0fdae09fae8'\n" + marker)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__ + ':generated', 'exec'))
