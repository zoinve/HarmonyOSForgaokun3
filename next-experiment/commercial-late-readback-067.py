"""Extend existing read-only probes into the real welcome/desktop interval."""
from pathlib import Path
import runpy

previous = runpy.run_path(str(Path(__file__).with_name('commercial-readback-035.py')))
GATE = r'''
#include <time.h>
static bool late_observation067(unsigned long long *next){
 const int saved067=errno;
 struct timespec now067={};
 if(clock_gettime(CLOCK_MONOTONIC,&now067)!=0){errno=saved067;return false;}
 if(now067.tv_sec<100 || now067.tv_sec>=145){errno=saved067;return false;}
 const unsigned long long stamp067=1000000000ULL*now067.tv_sec+now067.tv_nsec;
 unsigned long long expected067=__atomic_load_n(next,__ATOMIC_RELAXED);
 bool accepted067=false;
 if(stamp067>=expected067)
  accepted067=__atomic_compare_exchange_n(next,&expected067,stamp067+5000000000ULL,
   false,__ATOMIC_RELAXED,__ATOMIC_RELAXED);
 errno=saved067;return accepted067;
}
'''


def instrument(source):
    result = previous['instrument'](source)
    anchor = 'static void observe_dispatch033(){'
    assert result.count(anchor) == 1
    result = result.replace(anchor, GATE + '\n' + anchor, 1)
    old = ' if(sample033>16){errno=saved033;return;}'
    new = (' static unsigned long long next_dispatch067=0;\n'
           ' if(sample033>16 && !late_observation067(&next_dispatch067))'
           '{errno=saved033;return;}')
    assert result.count(old) == 1
    result = result.replace(old, new, 1)
    old = '            bool observe031=__atomic_fetch_add(&count031,1u,__ATOMIC_RELAXED)<8;'
    new = ('            static unsigned long long next_copy067=0;\n'
           '            bool observe031=__atomic_fetch_add(&count031,1u,__ATOMIC_RELAXED)<8\n'
           '                || late_observation067(&next_copy067);')
    assert result.count(old) == 1
    return result.replace(old, new, 1)
