"""Transform a retained RAM boot payload, not an original filesystem image."""


def gpu_overlay(source):
    anchor = '    if(chdir("/newroot") || mount(".","/",NULL,MS_MOVE,NULL) || chroot(".") || chdir("/")) die("switch root mount");'
    library_path = 'LD_LIBRARY_PATH=/system/lib64:/system/lib64/platformsdk:/system/lib64/chipset-sdk"'
    assert source.count(anchor) == 1
    assert source.count(library_path) == 1
    addition = r'''
    if(mount("/gpu883-libs","/newroot/system/lib64/lab-softpipe-167",NULL,MS_BIND,NULL))die("GPU directory bind");
    if(mount(NULL,"/newroot/system/lib64/lab-softpipe-167",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))die("GPU directory readonly");
    if(mount("/gpu883-libs/libEGL_impl.so","/newroot/system/lib64/libEGL_mesa.so",NULL,MS_BIND,NULL))die("GPU NativeWindow bridge bind");
    if(mount(NULL,"/newroot/system/lib64/libEGL_mesa.so",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))die("GPU bridge readonly");
    if(mount("/gpu883-libs/libgallium-25.0.1.so","/newroot/system/lib64/libgallium-25.0.1.so",NULL,MS_BIND,NULL))die("GPU gallium bind");
    if(mount(NULL,"/newroot/system/lib64/libgallium-25.0.1.so",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY,NULL))die("GPU gallium readonly");
    puts("GPU883_RAM_OVERLAY frontend_preserved=1 drawing_not_bypassed=1");fflush(stdout);
'''
    return source.replace(anchor, addition + anchor).replace(
        library_path, library_path[:-1] + ':/system/lib64/lab-softpipe-167"')
