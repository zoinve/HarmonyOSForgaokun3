"""Exact original rawfiles in a RAM-only, read-only preinstall overlay."""
from pathlib import PurePosixPath
import hashlib
import io
import stat
import zipfile

HAP_SHA256 = '392566ac1deefe9a269db3ebe45513038ed773f210e628f0ca55ce73ed34a1a7'
PREFIX = 'native-target/original-ui070/'


def rawfiles(data, expected=HAP_SHA256):
    assert hashlib.sha256(data).hexdigest() == expected, 'original HAP hash'
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert archive.testzip() is None, 'original ZIP CRC'
        result = {}
        for item in archive.infolist():
            if not item.filename.startswith('resources/rawfile/'):
                continue
            name = item.filename
            path = PurePosixPath(name)
            assert not path.is_absolute() and str(path) == name.rstrip('/')
            assert all(c not in ('', '.', '..') for c in name.rstrip('/').split('/'))
            assert all(c.isascii() and (c.isalnum() or c in '/._-') for c in name)
            assert not stat.S_ISLNK(item.external_attr >> 16)
            if item.is_dir():
                continue
            assert name not in result and item.file_size <= 8 * 1024 * 1024
            result[name] = archive.read(item)
        assert result and sum(map(len, result.values())) <= 16 * 1024 * 1024
        return result


def instrument(source, files):
    anchor = '    directory("/run/commercial-system005/upper/lib64",0755);'
    assert source.count(anchor) == 1
    target = '/run/commercial-system005/upper/app/HwStartupGuide'
    lines = [
        '    struct stat original070;',
        '    if(lstat("/system/app/HwStartupGuide/HwStartupGuide.hap",&original070) || !S_ISREG(original070.st_mode) || original070.st_size!=8838069)fail("original StartupGuide HAP required");',
        '    if(!lstat("/system/app/HwStartupGuide/resources",&original070) || errno!=ENOENT)fail("original rawfile layout must be absent");',
        '    directory("/run/commercial-system005/upper/app",0755);',
        '    directory("'+target+'",0755);',
    ]
    dirs = {str(parent) for name in files for parent in PurePosixPath(name).parents if str(parent) != '.'}
    for name in sorted(dirs, key=lambda x: (x.count('/'), x)):
        lines.append('    directory("'+target+'/'+name+'",0755);')
    for name in sorted(files):
        lines.append('    commercial_copy005("/original-ui070/'+name+'","'+target+'/'+name+'",0444);')
    lines.append('    dprintf(1,"COMMERCIAL070_ORIGINAL_RAWFILES files='+str(len(files))+' bytes='+str(sum(map(len, files.values())))+' original_hap_unchanged=1 ram_only=1 system_overlay_readonly=1 preinstall_path_hypothesis=1\\n");')
    return source.replace(anchor, '\n'.join(lines)+'\n'+anchor, 1)


def add_entries(entries, files):
    entries = dict(entries)
    additions = {}
    for name, data in sorted(files.items()):
        full = PREFIX + name
        for parent in reversed(PurePosixPath(full).parents):
            if str(parent) == '.':
                continue
            if str(parent) not in entries:
                entries[str(parent)] = (stat.S_IFDIR | 0o755, b'')
                additions[str(parent)] = entries[str(parent)]
            assert stat.S_ISDIR(entries[str(parent)][0])
        assert full not in entries
        entries[full] = (stat.S_IFREG | 0o444, data)
        additions[full] = entries[full]
    return entries, additions
