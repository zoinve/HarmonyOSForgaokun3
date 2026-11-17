from pathlib import Path

source = Path(__file__).with_name('test-commercial-hwbreak-050.py').read_text()
source = source.replace('commercial61-native-050', 'commercial61-native-052').replace('build-commercial-native-050.py', 'build-commercial-native-052.py').replace('commercial-hwbreak-050.h', 'commercial-hwbreak-052.py')
anchor = '    close(event.fd);free(memory);puts('
assert source.count(anchor) == 1
test = r'''
    char path[]="/tmp/hw052-XXXXXX";int original=mkstemp(path);assert(original>=0);assert(!unlink(path));
    size_t bytes=49152;unsigned char *contents=malloc(bytes);assert(contents);
    for(size_t i=0;i<bytes;++i)contents[i]=(unsigned char)(i*13+7);
    assert(write(original,contents,bytes)==(ssize_t)bytes);
    void *mapped=mmap(NULL,bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE,original,0);assert(mapped!=MAP_FAILED);
    int live=open("/proc/self/mem",O_RDONLY|O_CLOEXEC);assert(live>=0);
    uint64_t begin=(uint64_t)(uintptr_t)mapped;
    assert(hw052_mapping_equal(original,live,begin,0,bytes));
    assert(hw052_mapping_equal(original,live,begin+4096,4096,bytes-4096));
    size_t positions[]={0,16383,16384,32768,49151};
    for(unsigned i=0;i<sizeof(positions)/sizeof(positions[0]);++i){
        ((unsigned char *)mapped)[positions[i]]^=1;
        assert(!hw052_mapping_equal(original,live,begin,0,bytes) && errno==ENOEXEC);
        ((unsigned char *)mapped)[positions[i]]^=1;
    }
    assert(!hw052_mapping_equal(original,live,begin,bytes,1) && errno==EINVAL);
    assert(!hw052_mapping_equal(original,live,begin,0,0) && errno==EINVAL);
    assert(!hw052_mapping_equal(original,live,INT64_MAX,0,2) && errno==EINVAL);
    int empty=open("/dev/null",O_RDONLY);assert(empty>=0);
    assert(!hw052_mapping_equal(original,empty,begin,0,bytes) && errno==EIO);
    assert(!hw052_mapping_equal(original,-1,begin,0,bytes) && errno==EBADF);
    assert(mprotect(mapped,bytes,PROT_READ|PROT_EXEC)==0);
    assert(hw052_mapping_equal(original,live,begin,0,bytes));
    char maps_line[1024];FILE *self_maps=fopen("/proc/self/maps","r");assert(self_maps);
    int found=0;while(fgets(maps_line,sizeof(maps_line),self_maps)){
        unsigned long long start,end;
        if(sscanf(maps_line,"%llx-%llx",&start,&end)==2 && start==begin){found=1;break;}
    }
    fclose(self_maps);assert(found && hw052_mapping_unchanged(getpid(),maps_line));
    assert(mprotect(mapped,bytes,PROT_READ)==0);
    assert(!hw052_mapping_unchanged(getpid(),maps_line) && errno==EAGAIN);
    munmap(mapped,bytes);close(live);close(empty);close(original);free(contents);
'''
source = source.replace(anchor, test + anchor, 1)
source = source.replace('synthetic_ring_tests_passed=True,', 'synthetic_ring_tests_passed=True, executable_memory_tests_passed=True,')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
