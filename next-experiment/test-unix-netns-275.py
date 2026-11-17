import ctypes
import json
import os
import socket
import tempfile

if __name__ == '__main__':
    assert os.geteuid() == 0
    with tempfile.TemporaryDirectory(prefix='radio-netns275-') as directory:
        path = directory + '/endpoint'
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(path)
        server.listen(1)
        child = os.fork()
        if child == 0:
            libc = ctypes.CDLL(None, use_errno=True)
            if libc.unshare(0x40000000):
                os._exit(100)
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                client.connect(path)
                client.sendall(b'local-test')
                os._exit(0)
            except OSError as exc:
                os._exit(exc.errno)
        _, state = os.waitpid(child, 0)
        code = os.waitstatus_to_exitcode(state)
        print(json.dumps(dict(child_exit=code, cross_netns_path_socket_connected=code == 0,
                              target_device_modified=False)))
