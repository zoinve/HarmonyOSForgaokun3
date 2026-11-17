"""Add bounded association for the original commercial tokenless RPC parcels."""
from pathlib import Path

LEARNING = r'''
#include <unistd.h>
static bool connection_handle044(int fd,uint32_t handle,bool learn)
{
    unsigned pid=(unsigned)getpid();
    if(fd<0 || fd>65535 || handle>0xffffff || pid>0xffffff)return false;
    uint64_t key=(uint64_t(pid)<<40)|(uint64_t(unsigned(fd))<<24)|handle;
    static uint64_t known[128]={};
    for(unsigned i=0;i<128;++i){
        uint64_t value=__atomic_load_n(&known[i],__ATOMIC_RELAXED);
        if(value==key)return true;
        if(!value && learn){
            if(__atomic_compare_exchange_n(&known[i],&value,key,false,__ATOMIC_RELAXED,__ATOMIC_RELAXED))return true;
            if(value==key)return true;
        }
    }
    return false;
}
'''


def source():
    text = Path(__file__).with_name('commercial-binder-observer-043.h').read_text().replace('043', '044')
    text = text.replace('static unsigned snapshots044(', LEARNING + '\nstatic unsigned snapshots044(', 1)
    text = text.replace('BinderSnapshot044 *out, unsigned capacity)',
                        'BinderSnapshot044 *out, unsigned capacity, int fd = -1)', 1)
    anchor = '            if (type && found < capacity)'
    assert text.count(anchor) == 1
    text = text.replace(anchor, '''            if(type==1)connection_handle044(fd,transaction.target.handle,true);
            if(!type && (transaction.code==0 || transaction.code==17) &&
               connection_handle044(fd,transaction.target.handle,false))type=3;
''' + anchor, 1)
    text = text.replace('initial[12]', 'initial[18]').replace('late[12]', 'late[18]').replace('previous[12]', 'previous[18]')
    text = text.replace('snapshots044(*request, records, 16)', 'snapshots044(*request, records, 16, fd)')
    return text
