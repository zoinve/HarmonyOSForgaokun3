"""Preserve435 observation/auth and fix interrupted I/O and buffered close."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent


def broker451():
    source = runpy.run_path(str(BASE / 'test-bt-outcomes-437.py'))['broker435']()
    changes = [
        ('if(rc<0 || (p[0].revents&(POLLERR|POLLHUP|POLLNVAL)) || (p[1].revents&(POLLERR|POLLHUP|POLLNVAL)))break;',
         'if(rc<0 || (p[0].revents&POLLNVAL) || (p[1].revents&POLLNVAL))break;'),
        ('if(p[0].revents&POLLIN){\n            ssize_t n=recv(client,queued+count,sizeof(queued)-count,0);if(n<=0)break;',
         '''if(p[0].revents&(POLLIN|POLLHUP)){
            ssize_t n;
            do{n=recv(client,queued+count,sizeof(queued)-count,0);}while(n<0&&errno==EINTR);
            if(n<=0)break;'''),
        ('if(send(hci,queued,(size_t)size,MSG_NOSIGNAL)!=size)return;',
         '''ssize_t sent;
                do{sent=send(hci,queued,(size_t)size,MSG_NOSIGNAL);}while(sent<0&&errno==EINTR);
                if(sent!=size)return;'''),
        ('ssize_t n=recv(hci,packet,sizeof(packet),0);if(n<=0)break;',
         '''ssize_t n;
            do{n=recv(hci,packet,sizeof(packet),0);}while(n<0&&errno==EINTR);
            if(n<=0)break;'''),
        ('if(write_all(client,packet,(size_t)n))break;\n        }\n    }',
         '''if(write_all(client,packet,(size_t)n))break;
        }
        /* Consume queued readable bytes before handling terminal poll flags. */
        if((p[0].revents&POLLERR)||(p[1].revents&POLLERR)||
           ((p[1].revents&POLLHUP)&&!(p[1].revents&POLLIN)))break;
    }'''),
    ]
    for old, new in changes:
        assert source.count(old) == 1
        source = source.replace(old, new)
    return source
