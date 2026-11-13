"""Bounded diagnostic capture for the framebuffer path absent from QMP scanout."""
def frame_observer(source):
    old='/data/local/tmp/gpu898-frame.ppm'
    assert source.count(old)==1
    return source.replace(old,'/data/local/tmp/gpu913-capture/pending.ppm')+r'''
static void gpu913_observe(void) {
    pid_t child=fork();
    if(child<0){perror("GPU913 fork");return;}
    if(child)return;
    if(mkdir("/data/local/tmp/gpu913-capture",0700)){perror("GPU913 mkdir");_exit(125);}
    for(unsigned i=0;i<90;i++) {
        gpu898_snapshot();
        int rc=rename("/data/local/tmp/gpu913-capture/pending.ppm","/data/local/tmp/gpu913-capture/latest.ppm");
        printf("GPU913_CAPTURE index=%u rename_rc=%d errno=%d\n",i,rc,rc?errno:0);fflush(stdout);
        sleep(15);
    }
    _exit(0);
}
'''
