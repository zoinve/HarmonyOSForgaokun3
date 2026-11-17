"""Replace the truncated trace prefix with an existing bounded read-only stream."""
OLD = r'''        char perf016[32768];
        if(read_path("/data/native-perf-023.trace",perf016,sizeof(perf016))>0)dprintf(commercial_diag_fd003,"COMMERCIAL016_PERF sample=%u %s\n",sample,perf016);'''
NEW = '''        commercial_stream043("/data/native-perf-023.trace",sample,0,262144);'''


def repair(source):
    assert source.count(OLD) == 1, 'Expected exact historical prefix reader'
    return source.replace(OLD, NEW, 1)
