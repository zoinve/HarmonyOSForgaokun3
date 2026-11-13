"""RAM-only allocator integration: no disk or service identity changes."""
def allocator_overlay(source):
    anchor = '    if(chdir("/newroot") || mount(".","/",NULL,MS_MOVE,NULL) || chroot(".") || chdir("/")) die("switch root mount");'
    assert source.count(anchor) == 1
    change = '''    /* GPU907 allocator RAM-only overlay. */
    if(mount("/gpu883-libs/gpu905-buffer-vdi.so","/newroot/vendor/lib64/libdisplay_buffer_vdi_impl.z.so",NULL,MS_BIND,NULL))die("GPU907 allocator bind");
    if(mount(NULL,"/newroot/vendor/lib64/libdisplay_buffer_vdi_impl.z.so",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))die("GPU907 allocator readonly");
    puts("GPU907_ALLOCATOR_RAM_ONLY service_identity_preserved=1 no_kms_master=1");fflush(stdout);
    /* GPU907 allocator overlay end. */
'''
    return source.replace(anchor, change + anchor)
