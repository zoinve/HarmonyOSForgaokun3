"""Compile passive broker integration and test parsing without accessing HCI."""
from pathlib import Path
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent


def broker435():
    source = (BASE / 'native-qca-broker-022.c').read_text()
    replacements = [
        ('struct hci_address {', '#include "native-bt-outcomes-435.h"\nstruct hci_address {'),
        ('if(send(hci,queued,(size_t)size,MSG_NOSIGNAL)!=size)return;',
         '(void)bt340_command(queued,(size_t)size);\n                if(send(hci,queued,(size_t)size,MSG_NOSIGNAL)!=size)return;'),
        ('if(write_all(client,packet,(size_t)n))break;',
         '(void)bt435_event(packet,(size_t)n);\n            if(write_all(client,packet,(size_t)n))break;'),
        ('if(!write_all(client,&ack,1) && hci>=0)pump(client,hci);',
         'if(!write_all(client,&ack,1) && hci>=0){bt435_reset();pump(client,hci);bt435_summary();}'),
    ]
    for old, new in replacements:
        assert source.count(old) == 1
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='bt437-') as directory:
        stage = Path(directory)
        (stage / 'broker.c').write_text(broker435())
        subprocess.run(['aarch64-linux-gnu-gcc', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-static', '-I', str(BASE), str(stage / 'broker.c'),
                        '-o', str(stage / 'broker')], check=True)
        subprocess.run(['gcc', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                        '-fsanitize=address,undefined', '-I', str(BASE),
                        str(BASE / 'test-bt-outcomes-436.c'), '-o', str(stage / 'test')], check=True)
        output = subprocess.check_output([str(stage / 'test')], text=True, timeout=15)
        assert 'a5a5' not in output.lower()
        assert output.count('BT435_OUTCOME ') == 10
        print(output, end='')
        print('BT437 arm64_broker=pass target_hci_access=0')
