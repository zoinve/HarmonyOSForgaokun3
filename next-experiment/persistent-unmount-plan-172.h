#ifndef PERSISTENT_UNMOUNT_PLAN_172_H
#define PERSISTENT_UNMOUNT_PLAN_172_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PERSISTENT172_MAX_MOUNTS 1024
#define PERSISTENT172_PATH 4096
struct persistent172_mount {
    unsigned id, parent, major, minor;
    int selected, removed;
    char path[PERSISTENT172_PATH];
};

static int persistent172_decode(char *output, const char *input)
{
    size_t used = 0;
    while (*input) {
        unsigned char value = (unsigned char)*input++;
        if (value == '\\') {
            if (!strncmp(input,"040",3)) value = ' ';
            else if (!strncmp(input,"011",3)) value = '\t';
            else if (!strncmp(input,"012",3)) value = '\n';
            else if (!strncmp(input,"134",3)) value = '\\';
            else return -1;
            input += 3;
        }
        if (used + 1 >= PERSISTENT172_PATH) return -1;
        output[used++] = (char)value;
    }
    output[used] = 0;
    return used && output[0] == '/' ? 0 : -1;
}

static int persistent172_plan(FILE *stream, struct persistent172_mount *rows,
                              unsigned *count, unsigned major, unsigned minor)
{
    char line[16384], root[PERSISTENT172_PATH], path[PERSISTENT172_PATH];
    unsigned used = 0;
    while (fgets(line,sizeof(line),stream)) {
        if (!strchr(line,'\n') || used == PERSISTENT172_MAX_MOUNTS) return -1;
        struct persistent172_mount *row = rows + used;
        memset(row,0,sizeof(*row));
        int consumed = 0;
        if (sscanf(line,"%u %u %u:%u %4095s %4095s %n",&row->id,&row->parent,
                   &row->major,&row->minor,root,path,&consumed) != 6 || !row->id ||
            !strstr(line+consumed," - ") || persistent172_decode(row->path,path)) return -1;
        for (unsigned i=0;i<used;++i) if (rows[i].id == row->id) return -1;
        row->selected = (row->major == major && row->minor == minor) ||
            !strcmp(row->path,"/data") || !strncmp(row->path,"/data/",6);
        ++used;
    }
    if (ferror(stream) || !used) return -1;
    /* Include descendants of every data alias, even outside /data. */
    for (unsigned pass=0;pass<used;++pass) {
        int changed = 0;
        for (unsigned i=0;i<used;++i) {
            if (rows[i].selected) continue;
            for (unsigned j=0;j<used;++j) if (rows[j].selected && rows[i].parent == rows[j].id) {
                rows[i].selected = 1;
                changed = 1;
                break;
            }
        }
        if (!changed) break;
    }
    for (unsigned i=0;i<used;++i) if (rows[i].selected) {
        if (!strcmp(rows[i].path,"/")) return -1;
        /* An overmounted duplicate path cannot be targeted unambiguously. */
        for (unsigned j=0;j<used;++j)
            if (i != j && !strcmp(rows[i].path,rows[j].path)) return -1;
    }
    *count = used;
    return 0;
}

static int persistent172_next(struct persistent172_mount *rows, unsigned count)
{
    int pending = 0;
    for (unsigned i=0;i<count;++i) {
        if (!rows[i].selected || rows[i].removed) continue;
        pending = 1;
        int children = 0;
        for (unsigned j=0;j<count;++j)
            if (rows[j].selected && !rows[j].removed && rows[j].parent == rows[i].id) children = 1;
        if (!children) return (int)i;
    }
    return pending ? -2 : -1;
}
#endif
