"""Fresh read-only probe using mutually exclusive hilog query modes correctly."""
from pathlib import Path
base=Path(__file__).resolve().parent
builder=(base/'build-ui-diagnostics.py').read_text()
assert '/system/bin/hilog -x -z 300' in builder
builder=builder.replace('/system/bin/hilog -x -z 300','/system/bin/hilog -z 300')
builder=builder.replace("/system/bin/hilog -x -e '","/system/bin/hilog -e '")
builder=builder.replace('/system/bin/aa help; /system/bin/aa dump -h','/system/bin/aa dump -a -u 100; /system/bin/aa dump -l -u 100')
builder=builder.replace('LAB875','LAB876').replace('payload-875','payload-876').replace('command-probe-875','command-probe-876')
exec(compile(builder,str(base/'build-ui-diagnostics.py'),'exec'),{'__file__':str(base/'build-ui-diagnostics.py')})
