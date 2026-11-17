"""Correct our LOG_CORE domain; preserve the existing bounded instrumentation."""
from pathlib import Path
import runpy

previous=runpy.run_path(str(Path(__file__).with_name('commercial-egl-trace-025.py')))
HEADER=previous['HEADER'].replace('025','026').replace('0xD02610','0x0D002510')

def instrument(source):
    result=previous['instrument'](source)
    assert result.count(previous['HEADER'])==1
    return result.replace(previous['HEADER'],HEADER,1).replace('trace025','trace026').replace('drm_result025','drm_result026')
