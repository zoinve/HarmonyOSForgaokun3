/* Read-only guest display inspection; output belongs to this disposable run. */
#include <linux/fb.h>
#include <sys/ioctl.h>
static void gpu898_snapshot(void) {
    const char *paths[]={"/sys/kernel/debug/dri/0/state","/sys/class/graphics/fb0/virtual_size","/sys/class/graphics/fb0/stride"};
    for(unsigned i=0;i<sizeof(paths)/sizeof(paths[0]);i++) {
        char data[16385];int fd=open(paths[i],O_RDONLY|O_CLOEXEC);
        ssize_t n=fd<0?-1:read(fd,data,sizeof(data)-1);
        printf("GPU898_STATE path=%s bytes=%zd errno=%d\n",paths[i],n,n<0?errno:0);
        if(n>0){data[n]=0;printf("%s\n",data);}if(fd>=0)close(fd);
    }
    int fd=open("/dev/graphics/fb0",O_RDONLY|O_CLOEXEC);
    struct fb_var_screeninfo v;struct fb_fix_screeninfo f;
    if(fd<0){printf("GPU898_FB_OPEN errno=%d\n",errno);return;}
    if(ioctl(fd,FBIOGET_VSCREENINFO,&v)||ioctl(fd,FBIOGET_FSCREENINFO,&f)) {
        printf("GPU898_FB_IOCTL errno=%d\n",errno);close(fd);return;
    }
    printf("GPU898_FB size=%ux%u bpp=%u stride=%u bytes=%u offset=%u,%u\n",v.xres,v.yres,v.bits_per_pixel,f.line_length,f.smem_len,v.xoffset,v.yoffset);
    size_t count=(size_t)f.line_length*v.yres_virtual;
    if(v.bits_per_pixel!=32 || v.xres>4096 || v.yres>4096 || !count || count>64*1024*1024 || count>f.smem_len){close(fd);return;}
    unsigned char *data=malloc(count);if(!data){close(fd);return;}
    size_t got=0;while(got<count){ssize_t n=read(fd,data+got,count-got);if(n<=0)break;got+=(size_t)n;}close(fd);
    printf("GPU898_FB_READ bytes=%zu\n",got);
    if(got!=count){free(data);return;}
    int output=open("/data/local/tmp/gpu898-frame.ppm",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if(output<0){printf("GPU898_FB_SAVE errno=%d\n",errno);free(data);return;}
    FILE *image=fdopen(output,"wb");if(!image){close(output);free(data);return;}
    fprintf(image,"P6\n%u %u\n255\n",v.xres,v.yres);unsigned nonblack=0;int valid=1;
    for(unsigned y=0;y<v.yres;y++)for(unsigned x=0;x<v.xres;x++) {
        size_t offset=(size_t)(y+v.yoffset)*f.line_length+(x+v.xoffset)*4;
        if(offset+4>got){valid=0;continue;}unsigned pixel;memcpy(&pixel,data+offset,4);
        unsigned char rgb[3]={(pixel>>v.red.offset)&255,(pixel>>v.green.offset)&255,(pixel>>v.blue.offset)&255};
        if(rgb[0]||rgb[1]||rgb[2])nonblack++;
        if(fwrite(rgb,1,3,image)!=3)valid=0;
    }
    if(fclose(image))valid=0;
    printf("GPU898_FB_SAVED valid=%d nonblack=%u desktop_not_assumed=1\n",valid,nonblack);free(data);fflush(stdout);
}
