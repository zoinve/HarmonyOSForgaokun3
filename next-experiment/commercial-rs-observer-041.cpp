// Observe public original application transaction methods. Never inspect private objects.
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <functional>
#include <memory>
#include <string>
#include <utility>
static void record041(const char *stage,const void *object,unsigned long value=0)
{
    int saved=errno;static unsigned count=0;
    if(__atomic_add_fetch(&count,1u,__ATOMIC_RELAXED)<=192){
        using Print=int(*)(int,int,unsigned,const char*,const char*,...);
        static auto print=reinterpret_cast<Print>(dlsym(RTLD_DEFAULT,"HiLogPrint"));
        timespec t={};clock_gettime(CLOCK_MONOTONIC,&t);
        if(print)print(3,4,0x0D002511,"CommercialRS041",
            "RS041 stage=%{public}s pid=%{public}d uid=%{public}d object=%{public}p value=%{public}lu mono_us=%{public}llu original_calls_forwarded=1",
            stage,getpid(),getuid(),object,value,(unsigned long long)t.tv_sec*1000000+t.tv_nsec/1000);
    }
    errno=saved;
}
template<class Fn> static Fn original041(const char *symbol)
{
    int saved=errno;void *p=dlsym(RTLD_NEXT,symbol);
    if(!p){record041("original_symbol_missing_refuse",nullptr);abort();}
    errno=saved;return reinterpret_cast<Fn>(p);
}
__attribute__((constructor)) static void loaded041(){record041("observer_loaded",nullptr);}
namespace OHOS { namespace Rosen {
class RSUIContext;
class RSUIDirector {
public:
    void Init(bool,bool,std::shared_ptr<RSUIContext>);
    void FlushModifier();
    void SendMessages();
    void SendMessages(std::function<void()>);
    void SetRoot(unsigned long);
};
class RSTransactionProxy {public:void FlushImplicitTransaction(unsigned long,const std::string&,bool,unsigned long);};
class RSTransactionHandler {public:void FlushImplicitTransaction(unsigned long,const std::string&,bool,unsigned long);};
void RSUIDirector::Init(bool create,bool multi,std::shared_ptr<RSUIContext> context)
{
    using Fn=void(*)(RSUIDirector*,bool,bool,std::shared_ptr<RSUIContext>);
    static Fn fn=original041<Fn>("_ZN4OHOS5Rosen12RSUIDirector4InitEbbNSt3__h10shared_ptrINS0_11RSUIContextEEE");
    record041("director_init_enter",this,unsigned(create)+2*unsigned(multi)+4*unsigned(context!=nullptr));
    fn(this,create,multi,std::move(context));record041("director_init_return",this);
}
void RSUIDirector::SetRoot(unsigned long id)
{
    using Fn=void(*)(RSUIDirector*,unsigned long);
    static Fn fn=original041<Fn>("_ZN4OHOS5Rosen12RSUIDirector7SetRootEm");
    record041("director_setroot_enter",this,id);fn(this,id);record041("director_setroot_return",this,id);
}
void RSUIDirector::FlushModifier()
{
    using Fn=void(*)(RSUIDirector*);
    static Fn fn=original041<Fn>("_ZN4OHOS5Rosen12RSUIDirector13FlushModifierEv");
    record041("director_modifier_enter",this);fn(this);record041("director_modifier_return",this);
}
void RSUIDirector::SendMessages()
{
    using Fn=void(*)(RSUIDirector*);
    static Fn fn=original041<Fn>("_ZN4OHOS5Rosen12RSUIDirector12SendMessagesEv");
    record041("director_send_enter",this);fn(this);record041("director_send_return",this);
}
void RSUIDirector::SendMessages(std::function<void()> callback)
{
    using Fn=void(*)(RSUIDirector*,std::function<void()>);
    static Fn fn=original041<Fn>("_ZN4OHOS5Rosen12RSUIDirector12SendMessagesENSt3__h8functionIFvvEEE");
    record041("director_send_callback_enter",this,unsigned(bool(callback)));
    fn(this,std::move(callback));record041("director_send_callback_return",this);
}
#define FLUSH041(Class,Symbol,Tag) \
void Class::FlushImplicitTransaction(unsigned long stamp,const std::string &ability,bool sync,unsigned long syncTime) \
{ \
    using Fn=void(*)(Class*,unsigned long,const std::string&,bool,unsigned long); \
    static Fn fn=original041<Fn>(Symbol); \
    record041(Tag "_enter",this,stamp);fn(this,stamp,ability,sync,syncTime);record041(Tag "_return",this,stamp); \
}
FLUSH041(RSTransactionProxy,"_ZN4OHOS5Rosen18RSTransactionProxy24FlushImplicitTransactionEmRKNSt3__h12basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEEbm","proxy_flush")
FLUSH041(RSTransactionHandler,"_ZN4OHOS5Rosen20RSTransactionHandler24FlushImplicitTransactionEmRKNSt3__h12basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEEbm","handler_flush")
} }
