"""Extract actual original-service freeze reports from immutable retained run097."""
from pathlib import Path

source = Path(__file__).with_name('audit-original-sceneboard-freezes-096.py').read_text()
source = source.replace('baremetal-sdk-original-init-qemu-096', 'baremetal-sdk-original-init-qemu-097')
source = source.replace('reports/original-sceneboard-freezes-096', 'reports/original-render-freeze-097')
start = source.index('    selected = [')
end = source.index('    files = []', start)
source = source[:start] + '''    selected = [
        ('/log/faultlog/faultlogger/sysfreeze-render_service-1003-19700101080856693.log', 109720),
        ('/log/faultlog/faultlogger/appfreeze-com.ohos.sceneboard-20020034-19700101080834666.log', 536254),
    ]
''' + source[end:]
compile(source, 'original-render-freeze-097-extraction', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'original-render-freeze-097-extraction', 'exec'))
