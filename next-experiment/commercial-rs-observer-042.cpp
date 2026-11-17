// Observe public original application transaction methods. Never inspect private objects.
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <functional>
#include <memory>
#include <string>
#include <utility>
static void record042(const char *stage,const void *object,unsigned long value=0)
{
    int saved=errno;struct timespec t={};clock_gettime(CLOCK_MONOTONIC,&t);
    uint64_t now=uint64_t(t.tv_sec)*1000000+t.tv_nsec/1000;
    static const char *names[]={"observer_loaded","original_symbol_missing_refuse","director_init_enter","director_init_return","director_setroot_enter","director_setroot_return","director_modifier_enter","director_modifier_return","director_send_enter","director_send_return","director_send_callback_enter","director_send_callback_return","proxy_flush_enter","proxy_flush_return","handler_flush_enter","handler_flush_return","proxy_empty_before","proxy_empty_after","proxy_index_before","proxy_index_after","unirender_original_result","director_rsroot_enter","director_rsroot_return","director_rssurface_enter","director_rssurface_return","client_commit_enter","client_commit_return","hybrid_original_result","rpc_commit_enter","rpc_commit_return"};
    static unsigned attempts[30]={},late[30]={};static uint64_t previous[30]={};
    unsigned slot=0;while(slot<30 && strcmp(stage,names[slot]))++slot;
    bool emit=false;
    if(slot<30){
        unsigned n=__atomic_add_fetch(&attempts[slot],1u,__ATOMIC_RELAXED);
        emit=n<=6;
        if(!emit && now>=70000000 && __atomic_load_n(&late[slot],__ATOMIC_RELAXED)<16){
            uint64_t old=__atomic_load_n(&previous[slot],__ATOMIC_RELAXED);
            if(now-old>=5000000 && __atomic_compare_exchange_n(&previous[slot],&old,now,false,__ATOMIC_RELAXED,__ATOMIC_RELAXED)){
                __atomic_add_fetch(&late[slot],1u,__ATOMIC_RELAXED);emit=true;
            }
        }
    }
    if(emit){
        using Print=int(*)(int,int,unsigned,const char*,const char*,...);
        static auto print=reinterpret_cast<Print>(dlsym(RTLD_DEFAULT,"HiLogPrint"));
        if(print)print(3,4,0x0D002511,"CommercialRS042",
            "RS042 stage=%{public}s pid=%{public}d uid=%{public}d object=%{public}p value=%{public}lu mono_us=%{public}llu original_calls_forwarded=1",
            stage,getpid(),getuid(),object,value,(unsigned long long)now);
    }
    errno=saved;
}

template<class Fn> static Fn original042(const char *symbol)
{
    int saved=errno;void *p=dlsym(RTLD_NEXT,symbol);
    if(!p){record042("original_symbol_missing_refuse",nullptr);abort();}
    errno=saved;return reinterpret_cast<Fn>(p);
}
static void proxy_state042(const void *object,bool after)
{
    using Empty=bool(*)(const void*);using Index=uint32_t(*)(const void*);
    static auto empty=original042<Empty>("_ZNK4OHOS5Rosen18RSTransactionProxy7IsEmptyEv");
    static auto index=original042<Index>("_ZNK4OHOS5Rosen18RSTransactionProxy23GetTransactionDataIndexEv");
    int saved=errno;
    bool actual=empty(object);uint32_t sequence=index(object);
    record042(after?"proxy_empty_after":"proxy_empty_before",object,unsigned(actual));
    record042(after?"proxy_index_after":"proxy_index_before",object,sequence);
    errno=saved;
}
__attribute__((constructor)) static void loaded042(){record042("observer_loaded",nullptr);}
namespace OHOS { namespace Rosen {
class RSUIContext;class RSRootNode;class RSSurfaceNode;class RSTransactionData;
class RSUIDirector {
public:
    void Init(bool,bool,std::shared_ptr<RSUIContext>);
    void FlushModifier();
    void SendMessages();
    void SendMessages(std::function<void()>);
    void SetRoot(unsigned long);
    void SetRSRootNode(std::shared_ptr<RSRootNode>);
    void SetRSSurfaceNode(std::shared_ptr<RSSurfaceNode>);
};
class RSTransactionProxy {public:void FlushImplicitTransaction(unsigned long,const std::string&,bool,unsigned long);};
class RSTransactionHandler {public:void FlushImplicitTransaction(unsigned long,const std::string&,bool,unsigned long);};
void RSUIDirector::Init(bool create,bool multi,std::shared_ptr<RSUIContext> context)
{
    using Fn=void(*)(RSUIDirector*,bool,bool,std::shared_ptr<RSUIContext>);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen12RSUIDirector4InitEbbNSt3__h10shared_ptrINS0_11RSUIContextEEE");
    record042("director_init_enter",this,unsigned(create)+2*unsigned(multi)+4*unsigned(context!=nullptr));
    fn(this,create,multi,std::move(context));record042("director_init_return",this);
}
void RSUIDirector::SetRoot(unsigned long id)
{
    using Fn=void(*)(RSUIDirector*,unsigned long);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen12RSUIDirector7SetRootEm");
    record042("director_setroot_enter",this,id);fn(this,id);record042("director_setroot_return",this,id);
}
void RSUIDirector::FlushModifier()
{
    using Fn=void(*)(RSUIDirector*);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen12RSUIDirector13FlushModifierEv");
    record042("director_modifier_enter",this);fn(this);record042("director_modifier_return",this);
}
void RSUIDirector::SendMessages()
{
    using Fn=void(*)(RSUIDirector*);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen12RSUIDirector12SendMessagesEv");
    record042("director_send_enter",this);fn(this);record042("director_send_return",this);
}
void RSUIDirector::SendMessages(std::function<void()> callback)
{
    using Fn=void(*)(RSUIDirector*,std::function<void()>);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen12RSUIDirector12SendMessagesENSt3__h8functionIFvvEEE");
    record042("director_send_callback_enter",this,unsigned(bool(callback)));
    fn(this,std::move(callback));record042("director_send_callback_return",this);
}
#define FLUSH042(Class,Symbol,Tag) \
void Class::FlushImplicitTransaction(unsigned long stamp,const std::string &ability,bool sync,unsigned long syncTime) \
{ \
    using Fn=void(*)(Class*,unsigned long,const std::string&,bool,unsigned long); \
    static Fn fn=original042<Fn>(Symbol); \
    if(Tag[0]=='p')proxy_state042(this,false); \
    record042(Tag "_enter",this,stamp);fn(this,stamp,ability,sync,syncTime);record042(Tag "_return",this,stamp); \
    if(Tag[0]=='p')proxy_state042(this,true); \
}
FLUSH042(RSTransactionProxy,"_ZN4OHOS5Rosen18RSTransactionProxy24FlushImplicitTransactionEmRKNSt3__h12basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEEbm","proxy_flush")
FLUSH042(RSTransactionHandler,"_ZN4OHOS5Rosen20RSTransactionHandler24FlushImplicitTransactionEmRKNSt3__h12basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEEbm","handler_flush")

void RSUIDirector::SetRSRootNode(std::shared_ptr<RSRootNode> node)
{
    using Fn=void(*)(RSUIDirector*,std::shared_ptr<RSRootNode>);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen12RSUIDirector13SetRSRootNodeENSt3__h10shared_ptrINS0_10RSRootNodeEEE");
    record042("director_rsroot_enter",this,unsigned(node!=nullptr));fn(this,std::move(node));record042("director_rsroot_return",this);
}
void RSUIDirector::SetRSSurfaceNode(std::shared_ptr<RSSurfaceNode> node)
{
    using Fn=void(*)(RSUIDirector*,std::shared_ptr<RSSurfaceNode>);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen12RSUIDirector16SetRSSurfaceNodeENSt3__h10shared_ptrINS0_13RSSurfaceNodeEEE");
    record042("director_rssurface_enter",this,unsigned(node!=nullptr));fn(this,std::move(node));record042("director_rssurface_return",this);
}
class RSSystemProperties {public:static bool GetUniRenderEnabled();static bool GetHybridRenderEnabled();};
bool RSSystemProperties::GetUniRenderEnabled()
{
    using Fn=bool(*)();
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen18RSSystemProperties19GetUniRenderEnabledEv");
    bool value=fn();record042("unirender_original_result",nullptr,unsigned(value));return value;
}
class RSRenderServiceClient {public:void CommitTransaction(std::unique_ptr<RSTransactionData>&);};
void RSRenderServiceClient::CommitTransaction(std::unique_ptr<RSTransactionData> &data)
{
    using Fn=void(*)(RSRenderServiceClient*,std::unique_ptr<RSTransactionData>&);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen21RSRenderServiceClient17CommitTransactionERNSt3__h10unique_ptrINS0_17RSTransactionDataENS2_14default_deleteIS4_EEEE");
    record042("client_commit_enter",this,unsigned(data!=nullptr));fn(this,data);record042("client_commit_return",this,unsigned(data!=nullptr));
}


bool RSSystemProperties::GetHybridRenderEnabled()
{
    using Fn=bool(*)();
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen18RSSystemProperties22GetHybridRenderEnabledEv");
    bool value=fn();record042("hybrid_original_result",nullptr,unsigned(value));return value;
}
class RSRenderServiceConnectionProxy {public:void CommitTransaction(std::unique_ptr<RSTransactionData>&);};
void RSRenderServiceConnectionProxy::CommitTransaction(std::unique_ptr<RSTransactionData> &data)
{
    using Fn=void(*)(RSRenderServiceConnectionProxy*,std::unique_ptr<RSTransactionData>&);
    static Fn fn=original042<Fn>("_ZN4OHOS5Rosen30RSRenderServiceConnectionProxy17CommitTransactionERNSt3__h10unique_ptrINS0_17RSTransactionDataENS2_14default_deleteIS4_EEEE");
    record042("rpc_commit_enter",this,unsigned(data!=nullptr));fn(this,data);record042("rpc_commit_return",this,unsigned(data!=nullptr));
}

} }
