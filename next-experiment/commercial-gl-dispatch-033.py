"""Compare public original-frontend and Mesa queries on the actual swap thread."""
from pathlib import Path
import runpy
previous=runpy.run_path(str(Path(__file__).with_name('commercial-egl-pixels-031.py')))
QUERY=r'''
using String033=const GLubyte *(*)(GLenum);
using Integer033=void (*)(GLenum,GLint *);
struct State033 {
 const GLubyte *version=nullptr,*renderer=nullptr;
 GLint read_fbo=-1,draw_fbo=-1,program=-1,viewport[4]={-1,-1,-1,-1};
};
static State033 query033(String033 string_fn,Integer033 integer_fn){
 const int saved033=errno;State033 state;
 if(string_fn){state.version=string_fn(GL_VERSION);if(state.version)state.renderer=string_fn(GL_RENDERER);}
 if(state.version && integer_fn){
  integer_fn(GL_READ_FRAMEBUFFER_BINDING,&state.read_fbo);
  integer_fn(GL_DRAW_FRAMEBUFFER_BINDING,&state.draw_fbo);
  integer_fn(GL_CURRENT_PROGRAM,&state.program);integer_fn(GL_VIEWPORT,state.viewport);
 }
 errno=saved033;return state;
}
'''
OBSERVE=r'''
static void observe_dispatch033(){
 const int saved033=errno;
 static unsigned count033=0;
 unsigned sample033=__atomic_add_fetch(&count033,1u,__ATOMIC_RELAXED);
 if(sample033>16){errno=saved033;return;}
 // NOLOAD: do not manufacture a new frontend instance or initialize a different driver.
 static void *front_gl033=dlopen("/system/lib64/libGLESv3.so",RTLD_NOW|RTLD_LOCAL|RTLD_NOLOAD);
 static void *front_egl033=dlopen("/system/lib64/libEGL.so",RTLD_NOW|RTLD_LOCAL|RTLD_NOLOAD);
 static auto string033=front_gl033?reinterpret_cast<String033>(dlsym(front_gl033,"glGetString")):nullptr;
 static auto integer033=front_gl033?reinterpret_cast<Integer033>(dlsym(front_gl033,"glGetIntegerv")):nullptr;
 using Context033=EGLContext (*)();
 static auto front_current033=front_egl033?reinterpret_cast<Context033>(dlsym(front_egl033,"eglGetCurrentContext")):nullptr;
 auto mesa_current033=real<Context033>("eglGetCurrentContext");
 EGLContext front_context033=front_current033?front_current033():EGL_NO_CONTEXT;
 EGLContext mesa_context033=mesa_current033?mesa_current033():EGL_NO_CONTEXT;
 State033 front033=query033(string033,integer033);
 State033 mesa033=query033(&glGetString,&glGetIntegerv);
 Dl_info front_owner033={},mesa_owner033={};
 if(string033)(void)dladdr(reinterpret_cast<const void *>(string033),&front_owner033);
 (void)dladdr(reinterpret_cast<const void *>(&glGetString),&mesa_owner033);
 using Print033=int (*)(int,int,unsigned,const char *,const char *,...);
 static auto print033=reinterpret_cast<Print033>(dlsym(RTLD_DEFAULT,"HiLogPrint"));
 if(print033){
  const State033 states033[]={front033,mesa033};
  const char *routes033[]={"commercial_frontend","own_mesa"};
  const char *owners033[]={front_owner033.dli_fname,mesa_owner033.dli_fname};
  for(unsigned i033=0;i033<2;++i033){
   const auto &s033=states033[i033];
   print033(3,4,0x0D002510,"CommercialDispatch033",
    "DISPATCH033 sample=%{public}u route=%{public}s frontend_loaded=%{public}d frontend_context=%{public}p mesa_context=%{public}p owner=%{public}s version=%{public}s renderer=%{public}s read_fbo=%{public}d draw_fbo=%{public}d program=%{public}d viewport=%{public}d,%{public}d,%{public}d,%{public}d error_not_consumed=1",
    sample033,routes033[i033],int(front_gl033!=nullptr && front_egl033!=nullptr),
    front_context033,mesa_context033,owners033[i033]?owners033[i033]:"unavailable",
    s033.version?reinterpret_cast<const char *>(s033.version):"unavailable",
    s033.renderer?reinterpret_cast<const char *>(s033.renderer):"unavailable",
    s033.read_fbo,s033.draw_fbo,s033.program,s033.viewport[0],s033.viewport[1],s033.viewport[2],s033.viewport[3]);
  }
 }
 errno=saved033;
}
'''

def instrument(source):
    result=previous['instrument'](source)
    assert 'DISPATCH033' not in result
    anchor='static int probe031(GLuint framebuffer,GLenum buffer,int width,int height)'
    assert result.count(anchor)==1
    result=result.replace(anchor,QUERY+OBSERVE+'\n'+anchor,1)
    anchor='    PerfScope023 timing("egl_gpu_submit_025");'
    assert result.count(anchor)==1
    return result.replace(anchor,anchor+'\n    observe_dispatch033();',1)
