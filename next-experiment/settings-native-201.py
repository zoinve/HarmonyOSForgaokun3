'''Outer-only Settings request and non-relaxing teardown diagnostics.'''


def replace_once(source, old, new):
    assert source.count(old)==1,old
    return source.replace(old,new,1)


def outer201(source):
    old='/commercial61-native-197/bootstrap-runtime087'
    assert source.count(old)==5
    source=source.replace(old,'/commercial61-native-201/bootstrap-runtime087')
    source=replace_once(source,'static int network083_command(pid_t child, const char *mode)',
        '#include "settings-launch-201.h"\n\nstatic int network083_command(pid_t child, const char *mode)')
    return replace_once(source,'                if(i==10 || i==13)(void)network083_command(child,"events");',
        '                if(i==10)settings201_start(child);\n                if(i==10 || i==13)(void)network083_command(child,"events");')


def plan201(source):
    anchor='static int persistent172_decode(char *output, const char *input)'
    diagnostic='''static unsigned persistent201_plan_reason;
static int persistent201_reject(unsigned reason, unsigned rows)
{
    persistent201_plan_reason = reason;
    dprintf(1,"PERSISTENT201_PLAN_REFUSED reason=%u parsed_rows=%u raw_paths_exported=0\\n",reason,rows);
    return -1;
}

'''
    source=replace_once(source,anchor,diagnostic+anchor)
    source=replace_once(source,'    unsigned used = 0;\n    while (fgets(line,sizeof(line),stream)) {',
        '    unsigned used = 0;\n    persistent201_plan_reason = 0;\n    while (fgets(line,sizeof(line),stream)) {')
    changes=[
        ("if (!strchr(line,'\\n') || used == PERSISTENT172_MAX_MOUNTS) return -1;",
         "if (!strchr(line,'\\n')) return persistent201_reject(1,used);\n        if (used == PERSISTENT172_MAX_MOUNTS) return persistent201_reject(2,used);"),
        ('&row->major,&row->minor,root,path,&consumed) != 6 || !row->id ||\n            !strstr(line+consumed," - ") || persistent172_decode(row->path,path)) return -1;',
         '&row->major,&row->minor,root,path,&consumed) != 6) return persistent201_reject(3,used);\n        if (!row->id) return persistent201_reject(4,used);\n        if (!strstr(line+consumed," - ")) return persistent201_reject(5,used);\n        if (persistent172_decode(row->path,path)) return persistent201_reject(6,used);'),
        ('if (rows[i].id == row->id) return -1;','if (rows[i].id == row->id) return persistent201_reject(7,used);'),
        ('if (ferror(stream) || !used) return -1;',
         'if (ferror(stream)) return persistent201_reject(8,used);\n    if (!used) return persistent201_reject(9,used);'),
        ('if (!strcmp(rows[i].path,"/")) return -1;','if (!strcmp(rows[i].path,"/")) return persistent201_reject(10,used);'),
        ('if (i != j && !strcmp(rows[i].path,rows[j].path)) return -1;',
         'if (i != j && !strcmp(rows[i].path,rows[j].path)) return persistent201_reject(11,used);'),
    ]
    for old,new in changes:source=replace_once(source,old,new)
    return source


def lifecycle201(source):
    source=replace_once(source,'#include "persistent-unmount-plan-172.h"',
        '#include "persistent-unmount-plan-201.h"')
    changes=[
        ('    if (fd < 0) return -1;','    if (fd < 0) { dprintf(1,"PERSISTENT201_PLAN_OPEN_FAILED errno=%d\\n",errno); return -1; }'),
        ('    if (!stream) { close(fd); return -1; }',
         '    if (!stream) { dprintf(1,"PERSISTENT201_PLAN_STREAM_FAILED errno=%d\\n",errno); close(fd); return -1; }'),
        ('    if (fclose(stream)) result = -1;',
         '    if (fclose(stream)) { dprintf(1,"PERSISTENT201_PLAN_CLOSE_FAILED errno=%d\\n",errno); result = -1; }'),
        ('    if (!rows || persistent172_load_plan(procdir,rows,&count)) _exit(123);',
         '    if (!rows) { dprintf(1,"PERSISTENT201_PLAN_ALLOC_FAILED errno=%d\\n",errno); _exit(123); }\n    if (persistent172_load_plan(procdir,rows,&count)) _exit(123);'),
    ]
    for old,new in changes:source=replace_once(source,old,new)
    return source
