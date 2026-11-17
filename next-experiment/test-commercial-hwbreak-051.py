from pathlib import Path

source = Path(__file__).with_name('test-commercial-hwbreak-050.py').read_text()
source = source.replace('commercial61-native-050', 'commercial61-native-051').replace('build-commercial-native-050.py', 'build-commercial-native-051.py').replace('commercial-hwbreak-050.h', 'commercial-hwbreak-051.py')
anchor = '    close(event.fd);free(memory);puts('
assert source.count(anchor) == 1
test = r'''
    char path_a[]="/tmp/hw051-a-XXXXXX",path_b[]="/tmp/hw051-b-XXXXXX";
    int first=mkstemp(path_a),second=mkstemp(path_b);assert(first>=0 && second>=0);
    assert(!unlink(path_a) && !unlink(path_b));
    assert(write(first,"original",8)==8 && write(second,"original",8)==8);
    struct stat a,b;assert(!fstat(first,&a) && !fstat(second,&b) && a.st_ino!=b.st_ino);
    assert(hw050_files_equal(first,second));
    assert(pwrite(second,"X",1,3)==1 && !hw050_files_equal(first,second));
    close(first);close(second);
'''
source = source.replace(anchor, test + anchor, 1)
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, full_file_identity_tests_passed=True,')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
