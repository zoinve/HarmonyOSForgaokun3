"""Check Git's index, not generated files: text-only publication and Python syntax."""
import ast
from pathlib import PurePosixPath
import re
import subprocess
import sys

MAX_BYTES = 512 * 1024
SOURCE_SUFFIXES = {'.py', '.c', '.cpp', '.h', '.hpp', '.service', '.timer'}
SECRETS = re.compile(
    rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|'
    rb'gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|'
    rb'AKIA[0-9A-Z]{16}'
)


def validate_file(name: str, data: bytes) -> list[str]:
    p = PurePosixPath(name)
    parts = p.parts
    allowed = name in {'README.md', '.gitignore', '.gitattributes',
                       '.github/workflows/source-only.yml'}
    if len(parts) == 2 and parts[0] == 'next-experiment':
        allowed = p.suffix in SOURCE_SUFFIXES
    if len(parts) >= 2 and parts[0] == 'docs':
        allowed = p.suffix == '.md'
    if len(parts) == 2 and parts[0] == 'reports':
        allowed = p.suffix == '.md'
    if len(parts) == 2 and parts[0] == 'tools':
        allowed = p.suffix == '.py'
    errors = []
    if not allowed or p.is_absolute() or '..' in parts:
        errors.append('not in the source-only publication allowlist')
    if len(data) > MAX_BYTES:
        errors.append('exceeds the 512 KiB per-file limit')
    if b'\0' in data or data.startswith((b'\x7fELF', b'MZ', b'PK\x03\x04', b'\x1f\x8b')):
        errors.append('binary content is forbidden')
    if SECRETS.search(data):
        errors.append('possible credential/private key; inspect locally')
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        errors.append('not UTF-8 text')
    else:
        if p.suffix == '.py':
            try:
                ast.parse(text, filename=name)
            except SyntaxError as e:
                errors.append(f'Python syntax error on line {e.lineno}')
    return errors


def staged_files():
    names = subprocess.check_output(['git', 'ls-files', '-z']).decode('utf-8').split('\0')
    names = [name for name in names if name]
    # One batch process checks actual staged blobs, even if working files differ.
    result = subprocess.run(['git', 'cat-file', '--batch'],
                            input=''.join(':' + n + '\n' for n in names).encode(),
                            capture_output=True, check=True).stdout
    offset = 0
    for name in names:
        end = result.index(b'\n', offset)
        header = result[offset:end].split()
        if len(header) != 3 or header[1] != b'blob':
            raise RuntimeError(f'not a staged regular blob: {name}')
        size = int(header[2])
        offset = end + 1
        yield name, result[offset:offset + size]
        offset += size + 1


def main() -> int:
    count = total = failures = 0
    for name, data in staged_files():
        count += 1
        total += len(data)
        for error in validate_file(name, data):
            print(f'{name}: {error}', file=sys.stderr)
            failures += 1
    if not count:
        print('No staged/tracked source files found.', file=sys.stderr)
        return 1
    print(f'Checked {count} staged text files, {total:,} bytes; {failures} policy/syntax errors.')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
