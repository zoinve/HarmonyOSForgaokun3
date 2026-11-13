/* Native client-composition GPU path. Caller serializes all entry points.
 * No service impersonation, CPU readback, fake fence or front-buffer writes. */
#pragma once
#include "native-cursor-pixels-032.h"
#include <cstdio>
#include <cerrno>
#include <cstring>
#include <dlfcn.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/dma-buf.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl3.h>
#include <GLES2/gl2ext.h>
#include <gbm.h>
#include <drm_fourcc.h>

namespace NativeGpu041 {
#define GPU041_GL(X) \
 X(PFNGLGETSTRINGPROC,GetString) X(PFNGLGETERRORPROC,GetError) \
 X(PFNGLCREATESHADERPROC,CreateShader) X(PFNGLSHADERSOURCEPROC,ShaderSource) \
 X(PFNGLCOMPILESHADERPROC,CompileShader) X(PFNGLGETSHADERIVPROC,GetShaderiv) \
 X(PFNGLGETSHADERINFOLOGPROC,GetShaderInfoLog) X(PFNGLDELETESHADERPROC,DeleteShader) \
 X(PFNGLCREATEPROGRAMPROC,CreateProgram) X(PFNGLATTACHSHADERPROC,AttachShader) \
 X(PFNGLLINKPROGRAMPROC,LinkProgram) X(PFNGLGETPROGRAMIVPROC,GetProgramiv) \
 X(PFNGLGETPROGRAMINFOLOGPROC,GetProgramInfoLog) X(PFNGLDELETEPROGRAMPROC,DeleteProgram) \
 X(PFNGLUSEPROGRAMPROC,UseProgram) X(PFNGLGETUNIFORMLOCATIONPROC,GetUniformLocation) \
 X(PFNGLUNIFORM1IPROC,Uniform1i) X(PFNGLUNIFORM2IPROC,Uniform2i) \
 X(PFNGLUNIFORM3IPROC,Uniform3i) X(PFNGLUNIFORM4IPROC,Uniform4i) \
 X(PFNGLGENTEXTURESPROC,GenTextures) X(PFNGLBINDTEXTUREPROC,BindTexture) \
 X(PFNGLTEXPARAMETERIPROC,TexParameteri) X(PFNGLTEXIMAGE2DPROC,TexImage2D) \
 X(PFNGLDELETETEXTURESPROC,DeleteTextures) \
 X(PFNGLGENFRAMEBUFFERSPROC,GenFramebuffers) X(PFNGLBINDFRAMEBUFFERPROC,BindFramebuffer) \
 X(PFNGLFRAMEBUFFERTEXTURE2DPROC,FramebufferTexture2D) \
 X(PFNGLCHECKFRAMEBUFFERSTATUSPROC,CheckFramebufferStatus) \
 X(PFNGLDELETEFRAMEBUFFERSPROC,DeleteFramebuffers) \
 X(PFNGLGENRENDERBUFFERSPROC,GenRenderbuffers) X(PFNGLBINDRENDERBUFFERPROC,BindRenderbuffer) \
 X(PFNGLFRAMEBUFFERRENDERBUFFERPROC,FramebufferRenderbuffer) \
 X(PFNGLDELETERENDERBUFFERSPROC,DeleteRenderbuffers) \
 X(PFNGLVIEWPORTPROC,Viewport) X(PFNGLDRAWARRAYSPROC,DrawArrays) X(PFNGLFINISHPROC,Finish)
#define GPU041_DECLARE(type,name) static type p##name=nullptr;
GPU041_GL(GPU041_DECLARE)
#undef GPU041_DECLARE
static void *egl_lib=nullptr,*gbm_lib=nullptr;
static int render_fd=-1;
static gbm_device *device=nullptr;
static EGLDisplay display=EGL_NO_DISPLAY;
static EGLContext context=EGL_NO_CONTEXT;
static PFNEGLGETPROCADDRESSPROC getproc=nullptr;
static PFNEGLMAKECURRENTPROC make_current=nullptr;
static PFNEGLCREATEIMAGEKHRPROC create_image=nullptr;
static PFNEGLDESTROYIMAGEKHRPROC destroy_image=nullptr;
static PFNGLEGLIMAGETARGETTEXTURE2DOESPROC target_tex=nullptr;
static PFNGLEGLIMAGETARGETRENDERBUFFERSTORAGEOESPROC target_rb=nullptr;
static gbm_bo *(*bo_create)(gbm_device*,uint32_t,uint32_t,uint32_t,uint32_t)=nullptr;
static int (*bo_fd)(gbm_bo*)=nullptr;
static uint32_t (*bo_stride)(gbm_bo*)=nullptr;
static void (*bo_destroy)(gbm_bo*)=nullptr;
static GLuint prog=0,bg=0,bg_fbo=0;
static unsigned bg_width=0,bg_height=0;
static bool ready=false,background_valid=false;
struct Buffer {
 gbm_bo *bo=nullptr;int fd=-1;void *map=MAP_FAILED;size_t size=0;
 unsigned width=0,height=0,pitch=0;EGLImageKHR image=EGL_NO_IMAGE_KHR;
 GLuint rb=0,fbo=0;
};
static bool begin(){return make_current&&context!=EGL_NO_CONTEXT&&make_current(display,EGL_NO_SURFACE,EGL_NO_SURFACE,context);}
static void end(){if(make_current&&display!=EGL_NO_DISPLAY)make_current(display,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);}
static void invalidate(){background_valid=false;}
static GLuint shader(GLenum type,const char *text)
{
 GLuint s=pCreateShader(type);pShaderSource(s,1,&text,nullptr);pCompileShader(s);GLint ok=0;pGetShaderiv(s,GL_COMPILE_STATUS,&ok);
 if(!ok){char msg[2048];pGetShaderInfoLog(s,sizeof(msg),nullptr,msg);std::fprintf(stderr,"NATIVE_GPU041 shader: %s\n",msg);pDeleteShader(s);return 0;}return s;
}
static GLuint program()
{
 const char *vs="#version 300 es\nvoid main(){vec2 p[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));gl_Position=vec4(p[gl_VertexID],0,1);}";
 const char *fs="#version 300 es\nprecision highp float;precision highp int;uniform sampler2D source;uniform int mode;uniform ivec2 dim;uniform ivec4 crop;uniform ivec3 cursor;out vec4 color;"
 "void main(){ivec2 p=ivec2(gl_FragCoord.xy);ivec2 q=mode==0?crop.xy+ivec2(p.y*crop.z/dim.y,(dim.x-1-p.x)*crop.w/dim.x):p;color=vec4(texelFetch(source,q,0).rgb,1);"
 "if(mode==1&&cursor.z!=0){ivec2 l=ivec2(p.y,dim.x-1-p.x)-cursor.xy;int x=l.x;int y=l.y;"
 "if(x>=0&&x<24&&y>=0&&y<36){bool t=y<27&&x<=y*2/3;bool s=y>=18&&y<35&&x>=8+(y-18)/3&&x<=12+(y-18)/3;"
 "if(t||s){bool e=x==0||y==0||(t&&x>=y*2/3-1)||(s&&(x==8+(y-18)/3||x==12+(y-18)/3||y==34));color=vec4(e?vec3(0):vec3(1),1);}}}}";
 GLuint v=shader(GL_VERTEX_SHADER,vs),f=shader(GL_FRAGMENT_SHADER,fs);if(!v||!f){if(v)pDeleteShader(v);if(f)pDeleteShader(f);return 0;}
 GLuint p=pCreateProgram();pAttachShader(p,v);pAttachShader(p,f);pLinkProgram(p);pDeleteShader(v);pDeleteShader(f);
 GLint ok=0;pGetProgramiv(p,GL_LINK_STATUS,&ok);if(!ok){char msg[2048];pGetProgramInfoLog(p,sizeof(msg),nullptr,msg);std::fprintf(stderr,"NATIVE_GPU041 link: %s\n",msg);pDeleteProgram(p);return 0;}return p;
}
static void source_texture(GLuint t)
{
 pBindTexture(GL_TEXTURE_2D,t);pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
 pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);pTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
}
static void shutdown()
{
 background_valid=false;ready=false;
 if(begin()){
  if(bg_fbo)pDeleteFramebuffers(1,&bg_fbo);if(bg)pDeleteTextures(1,&bg);if(prog)pDeleteProgram(prog);end();
 }
 bg_fbo=bg=prog=0;bg_width=bg_height=0;
 if(context!=EGL_NO_CONTEXT&&egl_lib){auto f=reinterpret_cast<PFNEGLDESTROYCONTEXTPROC>(dlsym(egl_lib,"eglDestroyContext"));if(f)f(display,context);}
 context=EGL_NO_CONTEXT;
 if(display!=EGL_NO_DISPLAY&&egl_lib){auto f=reinterpret_cast<PFNEGLTERMINATEPROC>(dlsym(egl_lib,"eglTerminate"));if(f)f(display);}
 display=EGL_NO_DISPLAY;
 if(device&&gbm_lib){auto f=reinterpret_cast<void(*)(gbm_device*)>(dlsym(gbm_lib,"gbm_device_destroy"));if(f)f(device);}device=nullptr;
 if(render_fd>=0)close(render_fd);render_fd=-1;
 if(gbm_lib)dlclose(gbm_lib);if(egl_lib)dlclose(egl_lib);gbm_lib=egl_lib=nullptr;make_current=nullptr;
}
static bool initialize(const char *prefix)
{
 if(ready)return true;
 char path[512];std::snprintf(path,sizeof(path),"%slibEGL.so.1",prefix);egl_lib=dlopen(path,RTLD_NOW|RTLD_LOCAL);
 std::snprintf(path,sizeof(path),"%slibgbm.so.1",prefix);gbm_lib=dlopen(path,RTLD_NOW|RTLD_LOCAL);
 auto attempt=[&]()->bool {
  if(!egl_lib||!gbm_lib)return false;
#define GPU041_SYM(var,type,lib,name) var=reinterpret_cast<type>(dlsym(lib,name));if(!var)return false;
  GPU041_SYM(getproc,PFNEGLGETPROCADDRESSPROC,egl_lib,"eglGetProcAddress")
  GPU041_SYM(make_current,PFNEGLMAKECURRENTPROC,egl_lib,"eglMakeCurrent")
  auto create_device=reinterpret_cast<gbm_device*(*)(int)>(dlsym(gbm_lib,"gbm_create_device"));if(!create_device)return false;
  using CreateBo=gbm_bo*(*)(gbm_device*,uint32_t,uint32_t,uint32_t,uint32_t);
  GPU041_SYM(bo_create,CreateBo,gbm_lib,"gbm_bo_create")
  GPU041_SYM(bo_fd,int(*)(gbm_bo*),gbm_lib,"gbm_bo_get_fd")
  GPU041_SYM(bo_stride,uint32_t(*)(gbm_bo*),gbm_lib,"gbm_bo_get_stride")
  GPU041_SYM(bo_destroy,void(*)(gbm_bo*),gbm_lib,"gbm_bo_destroy")
  render_fd=open("/dev/dri/renderD128",O_RDWR|O_CLOEXEC);if(render_fd<0)return false;
  device=create_device(render_fd);if(!device)return false;
  auto platform=reinterpret_cast<PFNEGLGETPLATFORMDISPLAYEXTPROC>(getproc("eglGetPlatformDisplayEXT"));if(!platform)return false;
  display=platform(EGL_PLATFORM_GBM_KHR,device,nullptr);if(display==EGL_NO_DISPLAY)return false;
  auto init=reinterpret_cast<PFNEGLINITIALIZEPROC>(dlsym(egl_lib,"eglInitialize"));
  auto bind=reinterpret_cast<PFNEGLBINDAPIPROC>(dlsym(egl_lib,"eglBindAPI"));
  auto choose=reinterpret_cast<PFNEGLCHOOSECONFIGPROC>(dlsym(egl_lib,"eglChooseConfig"));
  auto create=reinterpret_cast<PFNEGLCREATECONTEXTPROC>(dlsym(egl_lib,"eglCreateContext"));
  if(!init||!bind||!choose||!create||!init(display,nullptr,nullptr)||!bind(EGL_OPENGL_ES_API))return false;
  EGLint attrs[]={EGL_SURFACE_TYPE,0,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT_KHR,EGL_NONE},count=0;EGLConfig config;
  if(!choose(display,attrs,&config,1,&count)||!count)return false;
  EGLint ca[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE};context=create(display,config,EGL_NO_CONTEXT,ca);if(!begin())return false;
#define GPU041_LOAD(type,name) p##name=reinterpret_cast<type>(getproc("gl" #name));if(!p##name)return false;
  GPU041_GL(GPU041_LOAD)
#undef GPU041_LOAD
  create_image=reinterpret_cast<PFNEGLCREATEIMAGEKHRPROC>(getproc("eglCreateImageKHR"));
  destroy_image=reinterpret_cast<PFNEGLDESTROYIMAGEKHRPROC>(getproc("eglDestroyImageKHR"));
  target_tex=reinterpret_cast<PFNGLEGLIMAGETARGETTEXTURE2DOESPROC>(getproc("glEGLImageTargetTexture2DOES"));
  target_rb=reinterpret_cast<PFNGLEGLIMAGETARGETRENDERBUFFERSTORAGEOESPROC>(getproc("glEGLImageTargetRenderbufferStorageOES"));
  if(!create_image||!destroy_image||!target_tex||!target_rb)return false;
  auto renderer=reinterpret_cast<const char*>(pGetString(GL_RENDERER));
  if(!renderer||!std::strstr(renderer,"FD690"))return false;
  prog=program();if(!prog)return false;
  std::fprintf(stderr,"NATIVE_GPU041 initialized uid=%d renderer=%s\n",getuid(),renderer);end();return true;
 };
 ready=attempt();if(!ready){std::fprintf(stderr,"NATIVE_GPU041 init_failed errno=%d\n",errno);shutdown();}return ready;
#undef GPU041_SYM
}
static EGLImageKHR import(int fd,unsigned w,unsigned h,unsigned pitch,unsigned format)
{
 EGLint a[]={EGL_WIDTH,EGLint(w),EGL_HEIGHT,EGLint(h),EGL_LINUX_DRM_FOURCC_EXT,EGLint(format),
 EGL_DMA_BUF_PLANE0_FD_EXT,fd,EGL_DMA_BUF_PLANE0_OFFSET_EXT,0,EGL_DMA_BUF_PLANE0_PITCH_EXT,EGLint(pitch),EGL_NONE};
 return create_image(display,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,nullptr,a);
}
static void release(Buffer &b)
{
 if(begin()){
  if(b.fbo)pDeleteFramebuffers(1,&b.fbo);if(b.rb)pDeleteRenderbuffers(1,&b.rb);
  if(b.image!=EGL_NO_IMAGE_KHR)destroy_image(display,b.image);end();
 }
 if(b.map!=MAP_FAILED)munmap(b.map,b.size);if(b.fd>=0)close(b.fd);if(b.bo&&bo_destroy)bo_destroy(b.bo);b=Buffer{};
}
static bool allocate(Buffer &b,unsigned w,unsigned h,unsigned format)
{
 if(!ready||!w||!h||w>16384||h>16384)return false;
 b.width=w;b.height=h;b.bo=bo_create(device,w,h,format,GBM_BO_USE_LINEAR|GBM_BO_USE_RENDERING|GBM_BO_USE_SCANOUT);
 if(!b.bo)return false;
 b.fd=bo_fd(b.bo);b.pitch=bo_stride(b.bo);off_t size=b.fd>=0?lseek(b.fd,0,SEEK_END):-1;
 if(b.fd<0||b.pitch<w*4||size<off_t(size_t(b.pitch)*h)){release(b);return false;}b.size=size;
 b.map=mmap(nullptr,b.size,PROT_READ|PROT_WRITE,MAP_SHARED,b.fd,0);
 if(b.map==MAP_FAILED||!begin()){release(b);return false;}
 b.image=import(b.fd,w,h,b.pitch,format);
 bool ok=b.image!=EGL_NO_IMAGE_KHR;
 if(ok){pGenRenderbuffers(1,&b.rb);pBindRenderbuffer(GL_RENDERBUFFER,b.rb);target_rb(GL_RENDERBUFFER,reinterpret_cast<GLeglImageOES>(b.image));
  pGenFramebuffers(1,&b.fbo);pBindFramebuffer(GL_FRAMEBUFFER,b.fbo);pFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_RENDERBUFFER,b.rb);
  ok=pCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE&&pGetError()==GL_NO_ERROR;}
 end();if(!ok)release(b);return ok;
}
static bool background(unsigned w,unsigned h)
{
 if(bg&&bg_width==w&&bg_height==h)return true;
 invalidate();if(bg_fbo)pDeleteFramebuffers(1,&bg_fbo);if(bg)pDeleteTextures(1,&bg);
 pGenTextures(1,&bg);source_texture(bg);pTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,w,h,0,GL_RGBA,GL_UNSIGNED_BYTE,nullptr);
 pGenFramebuffers(1,&bg_fbo);pBindFramebuffer(GL_FRAMEBUFFER,bg_fbo);pFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,bg,0);
 bg_width=w;bg_height=h;return pCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE;
}
static void draw_cursor(Buffer &out,const CursorSnapshot032 &c)
{
 pUseProgram(prog);pUniform1i(pGetUniformLocation(prog,"source"),0);pUniform2i(pGetUniformLocation(prog,"dim"),out.width,out.height);
 pViewport(0,0,out.width,out.height);source_texture(bg);pBindFramebuffer(GL_FRAMEBUFFER,out.fbo);
 pUniform1i(pGetUniformLocation(prog,"mode"),1);
 bool visible=c.visible&&c.screen==0&&c.x>=0&&c.y>=0&&c.x<int(out.height)&&c.y<int(out.width);
 pUniform3i(pGetUniformLocation(prog,"cursor"),c.x,c.y,visible);pDrawArrays(GL_TRIANGLES,0,3);
}
static bool frame(Buffer &out,int fd,unsigned w,unsigned h,unsigned pitch,unsigned format,int cx,int cy,int cw,int ch,const CursorSnapshot032 &c)
{
 if(!ready||fd<0||!out.fbo||cx<0||cy<0||cw<=0||ch<=0||uint64_t(cx)+cw>w||uint64_t(cy)+ch>h||pitch<uint64_t(w)*4)return false;
 if(!begin())return false;
 invalidate();while(pGetError()!=GL_NO_ERROR){} // This context is private to this helper.
 EGLImageKHR input=import(fd,w,h,pitch,format);GLuint tex=0;bool ok=false;
 if(input!=EGL_NO_IMAGE_KHR&&background(out.width,out.height)){
  pGenTextures(1,&tex);source_texture(tex);target_tex(GL_TEXTURE_2D,reinterpret_cast<GLeglImageOES>(input));
  pUseProgram(prog);pUniform1i(pGetUniformLocation(prog,"source"),0);pUniform1i(pGetUniformLocation(prog,"mode"),0);
  pUniform2i(pGetUniformLocation(prog,"dim"),out.width,out.height);pUniform4i(pGetUniformLocation(prog,"crop"),cx,cy,cw,ch);
  pViewport(0,0,out.width,out.height);pBindFramebuffer(GL_FRAMEBUFFER,bg_fbo);pDrawArrays(GL_TRIANGLES,0,3);
  draw_cursor(out,c);pFinish();ok=pGetError()==GL_NO_ERROR;
 }
 if(tex)pDeleteTextures(1,&tex);if(input!=EGL_NO_IMAGE_KHR)destroy_image(display,input);
 background_valid=ok;end();return ok;
}
static bool repaint(Buffer &out,const CursorSnapshot032 &c)
{
 if(!ready||!background_valid||!out.fbo||out.width!=bg_width||out.height!=bg_height||!begin())return false;
 draw_cursor(out,c);pFinish();bool ok=pGetError()==GL_NO_ERROR;end();return ok;
}
} // namespace NativeGpu041
