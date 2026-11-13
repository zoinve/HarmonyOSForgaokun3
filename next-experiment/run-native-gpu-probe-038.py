from pathlib import Path
source=Path(__file__).with_name('run-native-gpu-probe-036.py').read_text().replace('native-gpu-probe-036','native-gpu-probe-038')
source=source.replace('import base64,hashlib,json,subprocess','import base64,hashlib,json,subprocess,os')
source=source.replace("['sudo','-n','timeout','60',str(p)]","['sudo','-n','env','EGL_LOG_LEVEL=debug','MESA_DEBUG=1','timeout','60',str(p)]")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
