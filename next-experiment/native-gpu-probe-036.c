/* Offscreen capability/pixel probe only: no modeset, no injected input, no desktop FPS claim. */
#define _GNU_SOURCE
#include <assert.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl3.h>
#include <GLES2/gl2ext.h>
#include <gbm.h>
#include <libdrm/drm.h>
#include <libdrm/drm_mode.h>
#include <libdrm/drm_fourcc.h>
#include <linux/dma-buf.h>

#define GL_FUNCTIONS(X) \
 X(PFNGLGETSTRINGPROC,GetString) X(PFNGLGETERRORPROC,GetError) \
 X(PFNGLCREATESHADERPROC,CreateShader) X(PFNGLSHADERSOURCEPROC,ShaderSource) \
 X(PFNGLCOMPILESHADERPROC,CompileShader) X(PFNGLGETSHADERIVPROC,GetShaderiv) \
 X(PFNGLGETSHADERINFOLOGPROC,GetShaderInfoLog) X(PFNGLCREATEPROGRAMPROC,CreateProgram) \
 X(PFNGLATTACHSHADERPROC,AttachShader) X(PFNGLLINKPROGRAMPROC,LinkProgram) \
 X(PFNGLGETPROGRAMIVPROC,GetProgramiv) X(PFNGLGETPROGRAMINFOLOGPROC,GetProgramInfoLog) \
 X(PFNGLUSEPROGRAMPROC,UseProgram) X(PFNGLGETUNIFORMLOCATIONPROC,GetUniformLocation) \
 X(PFNGLUNIFORM1IPROC,Uniform1i) X(PFNGLUNIFORM3IPROC,Uniform3i) \
 X(PFNGLGENTEXTURESPROC,GenTextures) X(PFNGLBINDTEXTUREPROC,BindTexture) \
 X(PFNGLTEXPARAMETERIPROC,TexParameteri) X(PFNGLTEXIMAGE2DPROC,TexImage2D) \
 X(PFNGLGENFRAMEBUFFERSPROC,GenFramebuffers) X(PFNGLBINDFRAMEBUFFERPROC,BindFramebuffer) \
 X(PFNGLFRAMEBUFFERTEXTURE2DPROC,FramebufferTexture2D) \
 X(PFNGLCHECKFRAMEBUFFERSTATUSPROC,CheckFramebufferStatus) \
 X(PFNGLGENRENDERBUFFERSPROC,GenRenderbuffers) X(PFNGLBINDRENDERBUFFERPROC,BindRenderbuffer) \
 X(PFNGLFRAMEBUFFERRENDERBUFFERPROC,FramebufferRenderbuffer) \
 X(PFNGLVIEWPORTPROC,Viewport) X(PFNGLDRAWARRAYSPROC,DrawArrays) X(PFNGLFINISHPROC,Finish)
#define DECLARE(type,name) static type p##name;
GL_FUNCTIONS(DECLARE)
#undef DECLARE
static PFNEGLGETPROCADDRESSPROC getproc;
static PFNEGLCREATEIMAGEKHRPROC create_image;
static PFNEGLDESTROYIMAGEKHRPROC destroy_image;
static PFNGLEGLIMAGETARGETTEXTURE2DOESPROC target_tex;
static PFNGLEGLIMAGETARGETRENDERBUFFERSTORAGEOESPROC target_rb;
static EGLDisplay display;
static int card;

static void *required(void *lib,const char *name)
{void *p=dlsym(lib,name);if(!p){fprintf(stderr,"missing %s: %s\n",name,dlerror());exit(2);}return p;}
static uint64_t now_us(void)
{struct timespec t;assert(!clock_gettime(CLOCK_MONOTONIC,&t));return (uint64_t)t.tv_sec*1000000+t.tv_nsec/1000;}
static void dma_sync(int fd,uint64_t flags)
{struct dma_buf_sync s={.flags=flags};assert(!ioctl(fd,DMA_BUF_IOCTL_SYNC,&s));}
struct image { unsigned width,height,pitch,handle;int fd;size_t size;unsigned char *map;EGLImageKHR egl; };
static struct image make_image(unsigned width,unsigned height,unsigned fourcc)
{
 struct drm_mode_create_dumb c={.width=width,.height=height,.bpp=32};assert(!ioctl(card,DRM_IOCTL_MODE_CREATE_DUMB,&c));
 struct drm_prime_handle p={.handle=c.handle,.flags=DRM_CLOEXEC|DRM_RDWR};assert(!ioctl(card,DRM_IOCTL_PRIME_HANDLE_TO_FD,&p));
 struct drm_mode_map_dumb m={.handle=c.handle};assert(!ioctl(card,DRM_IOCTL_MODE_MAP_DUMB,&m));
 unsigned char *map=mmap(NULL,c.size,PROT_READ|PROT_WRITE,MAP_SHARED,card,m.offset);assert(map!=MAP_FAILED);
 EGLint a[]={EGL_WIDTH,(EGLint)width,EGL_HEIGHT,(EGLint)height,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)fourcc,
  EGL_DMA_BUF_PLANE0_FD_EXT,p.fd,EGL_DMA_BUF_PLANE0_OFFSET_EXT,0,EGL_DMA_BUF_PLANE0_PITCH_EXT,(EGLint)c.pitch,EGL_NONE};
 EGLImageKHR e=create_image(display,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,a);assert(e!=EGL_NO_IMAGE_KHR);
 return (struct image){width,height,c.pitch,c.handle,p.fd,c.size,map,e};
}
static void free_image(struct image *i)
{
 assert(destroy_image(display,i->egl));assert(!munmap(i->map,i->size));assert(!close(i->fd));
 struct drm_mode_destroy_dumb d={.handle=i->handle};assert(!ioctl(card,DRM_IOCTL_MODE_DESTROY_DUMB,&d));
}
static GLuint shader(GLenum type,const char *source)
{
 GLuint id=pCreateShader(type);pShaderSource(id,1,&source,NULL);pCompileShader(id);GLint ok=0;pGetShaderiv(id,GL_COMPILE_STATUS,&ok);
 if(!ok){char log[4096];pGetShaderInfoLog(id,sizeof(log),NULL,log);fprintf(stderr,"shader: %s\n",log);exit(3);}return id;
}
static GLuint program(void)
{
 const char *vs="#version 300 es\nvoid main(){vec2 p[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));gl_Position=vec4(p[gl_VertexID],0,1);}";
 const char *fs="#version 300 es\nprecision highp float;precision highp int;uniform sampler2D source;uniform int mode;uniform int pw;uniform ivec3 cursor;out vec4 color;"
  "void main(){ivec2 p=ivec2(gl_FragCoord.xy);ivec2 q=mode==0?ivec2(p.y,pw-1-p.x):p;color=vec4(texelFetch(source,q,0).rgb,1);"
  "if(mode==1&&cursor.z!=0){ivec2 l=ivec2(p.y,pw-1-p.x)-cursor.xy;int x=l.x;int y=l.y;"
  "if(x>=0&&x<24&&y>=0&&y<36){bool t=y<27&&x<=y*2/3;bool s=y>=18&&y<35&&x>=8+(y-18)/3&&x<=12+(y-18)/3;"
  "if(t||s){bool e=x==0||y==0||(t&&x>=y*2/3-1)||(s&&(x==8+(y-18)/3||x==12+(y-18)/3||y==34));color=vec4(e?vec3(0):vec3(1),1);}}}}";
 GLuint id=pCreateProgram();pAttachShader(id,shader(GL_VERTEX_SHADER,vs));pAttachShader(id,shader(GL_FRAGMENT_SHADER,fs));pLinkProgram(id);
 GLint ok=0;pGetProgramiv(id,GL_LINK_STATUS,&ok);if(!ok){char log[4096];pGetProgramInfoLog(id,sizeof(log),NULL,log);fprintf(stderr,"program: %s\n",log);exit(4);}return id;
}
static void source_texture(GLuint texture)
{pBindTexture(GL_TEXTURE_2D,texture);pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);}
static void render(GLuint prog,GLuint input,GLuint background,GLuint bg_fbo,GLuint out_fbo,unsigned pw,unsigned ph,int x,int y,int visible)
{
 pUseProgram(prog);pUniform1i(pGetUniformLocation(prog,"source"),0);pUniform1i(pGetUniformLocation(prog,"pw"),(GLint)pw);
 pViewport(0,0,(GLsizei)pw,(GLsizei)ph);source_texture(input);pBindFramebuffer(GL_FRAMEBUFFER,bg_fbo);
 pUniform1i(pGetUniformLocation(prog,"mode"),0);pDrawArrays(GL_TRIANGLES,0,3);
 source_texture(background);pBindFramebuffer(GL_FRAMEBUFFER,out_fbo);pUniform1i(pGetUniformLocation(prog,"mode"),1);
 pUniform3i(pGetUniformLocation(prog,"cursor"),x,y,visible);pDrawArrays(GL_TRIANGLES,0,3);pFinish();assert(pGetError()==GL_NO_ERROR);
}
static void verify(const struct image *src,const struct image *out,int cx,int cy,int visible)
{
 dma_sync(src->fd,DMA_BUF_SYNC_START|DMA_BUF_SYNC_READ);
 dma_sync(out->fd,DMA_BUF_SYNC_START|DMA_BUF_SYNC_READ);
 for(unsigned y=0;y<out->height;++y)for(unsigned x=0;x<out->width;++x){
  unsigned lx=y,ly=out->width-1-x;const unsigned char *s=src->map+(size_t)ly*src->pitch+lx*4;
  unsigned char expected[4]={s[2],s[1],s[0],255};int dx=(int)lx-cx,dy=(int)ly-cy;
  if(visible&&dx>=0&&dx<24&&dy>=0&&dy<36){
   int t=dy<27&&dx<=dy*2/3,st=dy>=18&&dy<35&&dx>=8+(dy-18)/3&&dx<=12+(dy-18)/3;
   if(t||st){int edge=dx==0||dy==0||(t&&dx>=dy*2/3-1)||(st&&(dx==8+(dy-18)/3||dx==12+(dy-18)/3||dy==34));expected[0]=expected[1]=expected[2]=edge?0:255;}
  }
  const unsigned char *actual=out->map+(size_t)y*out->pitch+x*4;
  if(memcmp(actual,expected,3)){fprintf(stderr,"pixel mismatch at %u,%u got %u,%u,%u expected %u,%u,%u\n",x,y,actual[0],actual[1],actual[2],expected[0],expected[1],expected[2]);exit(5);}
 }
 dma_sync(out->fd,DMA_BUF_SYNC_END|DMA_BUF_SYNC_READ);
 dma_sync(src->fd,DMA_BUF_SYNC_END|DMA_BUF_SYNC_READ);
}
int main(void)
{
 setvbuf(stdout,NULL,_IONBF,0);card=open("/dev/dri/card0",O_RDWR|O_CLOEXEC);assert(card>=0);
 int render_fd=open("/dev/dri/renderD128",O_RDWR|O_CLOEXEC);assert(render_fd>=0);
 void *egl=dlopen("libEGL.so.1",RTLD_NOW|RTLD_LOCAL),*gbm=dlopen("libgbm.so.1",RTLD_NOW|RTLD_LOCAL);assert(egl&&gbm);
 getproc=(PFNEGLGETPROCADDRESSPROC)required(egl,"eglGetProcAddress");
 struct gbm_device *(*create_gbm)(int)=(void*)required(gbm,"gbm_create_device");struct gbm_device *device=create_gbm(render_fd);assert(device);
 PFNEGLGETPLATFORMDISPLAYEXTPROC platform=(void*)getproc("eglGetPlatformDisplayEXT");assert(platform);
 display=platform(EGL_PLATFORM_GBM_KHR,device,NULL);assert(display!=EGL_NO_DISPLAY);
 PFNEGLINITIALIZEPROC initialize=(void*)required(egl,"eglInitialize");assert(initialize(display,NULL,NULL));
 PFNEGLBINDAPIPROC bind_api=(void*)required(egl,"eglBindAPI");assert(bind_api(EGL_OPENGL_ES_API));
 EGLint config_attr[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT_KHR,EGL_NONE};EGLConfig config;EGLint count;
 PFNEGLCHOOSECONFIGPROC choose=(void*)required(egl,"eglChooseConfig");assert(choose(display,config_attr,&config,1,&count)&&count);
 EGLint context_attr[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE};PFNEGLCREATECONTEXTPROC create_context=(void*)required(egl,"eglCreateContext");
 EGLContext context=create_context(display,config,EGL_NO_CONTEXT,context_attr);assert(context!=EGL_NO_CONTEXT);
 PFNEGLMAKECURRENTPROC make_current=(void*)required(egl,"eglMakeCurrent");assert(make_current(display,EGL_NO_SURFACE,EGL_NO_SURFACE,context));
#define LOAD(type,name) p##name=(type)getproc("gl" #name);assert(p##name);
 GL_FUNCTIONS(LOAD)
#undef LOAD
 create_image=(void*)getproc("eglCreateImageKHR");destroy_image=(void*)getproc("eglDestroyImageKHR");
 target_tex=(void*)getproc("glEGLImageTargetTexture2DOES");target_rb=(void*)getproc("glEGLImageTargetRenderbufferStorageOES");assert(create_image&&destroy_image&&target_tex&&target_rb);
 const char *renderer=(const char*)pGetString(GL_RENDERER);printf("renderer=%s vendor=%s version=%s\n",renderer,pGetString(GL_VENDOR),pGetString(GL_VERSION));
 assert(renderer&&strstr(renderer,"FD690"));GLuint prog=program();
 for(unsigned pass=0;pass<2;++pass){
  unsigned pw=pass?1600:64,ph=pass?2560:80;struct image src=make_image(ph,pw,DRM_FORMAT_ABGR8888),out=make_image(pw,ph,DRM_FORMAT_XRGB8888);
  dma_sync(src.fd,DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);
  for(unsigned y=0;y<src.height;++y)for(unsigned x=0;x<src.width;++x){unsigned char *p=src.map+(size_t)y*src.pitch+x*4;p[0]=(x*13+y*3)&255;p[1]=(x+y*17)&255;p[2]=(x*7+y*11)&255;p[3]=255;}
  dma_sync(src.fd,DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);
  GLuint input,bg,bg_fbo,out_fbo,rb;pGenTextures(1,&input);source_texture(input);target_tex(GL_TEXTURE_2D,(GLeglImageOES)src.egl);
  pGenTextures(1,&bg);source_texture(bg);pTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,(GLsizei)pw,(GLsizei)ph,0,GL_RGBA,GL_UNSIGNED_BYTE,NULL);
  pGenFramebuffers(1,&bg_fbo);pBindFramebuffer(GL_FRAMEBUFFER,bg_fbo);pFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,bg,0);assert(pCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE);
  pGenRenderbuffers(1,&rb);pBindRenderbuffer(GL_RENDERBUFFER,rb);target_rb(GL_RENDERBUFFER,(GLeglImageOES)out.egl);
  pGenFramebuffers(1,&out_fbo);pBindFramebuffer(GL_FRAMEBUFFER,out_fbo);pFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_RENDERBUFFER,rb);assert(pCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE);
  const int corners[5][2]={{0,0},{(int)ph-1,0},{0,(int)pw-1},{(int)ph-1,(int)pw-1},{17,19}};
  for(unsigned n=0;n<5;++n){render(prog,input,bg,bg_fbo,out_fbo,pw,ph,corners[n][0],corners[n][1],1);verify(&src,&out,corners[n][0],corners[n][1],1);}
  render(prog,input,bg,bg_fbo,out_fbo,pw,ph,17,19,0);verify(&src,&out,17,19,0);
  uint64_t start=now_us();for(unsigned n=0;n<24;++n)render(prog,input,bg,bg_fbo,out_fbo,pw,ph,17,19,1);
  printf("GPU_PROBE036 pixels_verified=1 width=%u height=%u iterations=24 two_pass_glfinish_mean_us=%.2f modeset=0 desktop_fps_verified=0\n",pw,ph,(now_us()-start)/24.0);
  /* GL resources intentionally die with this short-lived diagnostic context. */
  free_image(&src);free_image(&out);
 }
 puts("PASS: hardware rotation, exact RGB, cursor edges and hide; offscreen only");return 0;
}
