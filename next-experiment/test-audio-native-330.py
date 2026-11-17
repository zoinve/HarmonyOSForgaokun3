"""New329 transport regression plus the existing platform contract tests."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__=='__main__':
 source=(BASE/'test-audio-native-320.py').read_text()
 source=source.replace('audio-native-test-320.json','audio-native-test-330.json')
 anchor="  subprocess.run(['aarch64-linux-gnu-gcc'"
 extra="""  subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    str(BASE/'test-audio-idle-329.c'),'-ldl','-o',str(stage/'idle-test')],check=True)
  idle=subprocess.run([str(stage/'idle-test')],capture_output=True,text=True,check=True,timeout=15)
"""
 assert source.count(anchor)==1
 source=source.replace(anchor,extra+anchor)
 source=source.replace('client_stdout=client.stdout,server_stdout=server.stdout,',
   'client_stdout=client.stdout,server_stdout=server.stdout,idle_stdout=idle.stdout,')
 exec(compile(source,'test-audio-native-330.generated.py','exec'),
   dict(__name__='__main__',__file__=str(BASE/'test-audio-native-330.generated.py')))
