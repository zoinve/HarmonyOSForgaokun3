"""Independent read-only preservation / original queue evidence checks."""
from pathlib import Path
import runpy


def launcher_source():
    source = runpy.run_path(str(Path(__file__).with_name('verify-composer-fd-001.py')), run_name='offline_generator')['launcher_source']()
    for old, new in [('composer-fd-001-independent-verification', 'composer-queue-001-independent-verification'),
                     ('composer-fd-package-001', 'composer-queue-package-001'),
                     ('composer-fd-run-001', 'composer-queue-run-001'),
                     ('composer-fd-runtime-001', 'composer-queue-runtime-001'),
                     ('FD001_CASE ', 'QUEUE001_CASE '), ('FD001_PASS ', 'QUEUE001_PASS '),
                     ('fd_ownership_only=True', 'original_queue_only=True')]:
        assert old in source, old
        source = source.replace(old, new)
    old = "    assert text.count('QUEUE001_PASS cases=8 ') == 1"
    assert source.count(old) == 1
    source = source.replace(old, "    assert text.count('QUEUE001_PASS cases=8 original_code=1 factory_called=0 composer_request_not_tested=1 desktop_not_tested=1') == 1\n    assert result['probe_pass'] is False  # Archived launcher expected the obsolete FD-only suffix.\n    assert result['child_exit_zero'] is True")
    source = source.replace('original_queue_only=True,', 'launcher_marker_mismatch=True, original_queue_only=True,')
    marker = '    table = bytes_at(0x62f2, 18)'
    assert source.count(marker) == 1
    source = source.replace(marker, "    for va, words in [(0x1a110, (0xa9bd7bfd,0xa90157f6,0xa9024ff4,0x910003fd)), (0x1a648, (0xa9be7bfd,0xa9014ff4,0x910003fd,0xaa0003f3)), (0x1b15c, (0xd10183ff,0xa9017bfd,0xa90267fa,0xa9035ff8)), (0x23144, (0xd10183ff,0xa9017bfd,0xa90267fa,0xa9035ff8))]:\n        assert bytes_at(va, 16) == struct.pack('<4I', *words)\n" + marker)
    return source


if __name__ == '__main__':
    exec(compile(launcher_source(), __file__ + ':generated', 'exec'))
