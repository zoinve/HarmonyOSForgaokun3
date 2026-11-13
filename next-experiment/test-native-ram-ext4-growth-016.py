"""Exercise genuine ext4 online growth on an exclusively owned disposable loop image."""
import subprocess
payload=r'''
import os,tempfile,pathlib,subprocess,fcntl,struct,json
def run(*args):return subprocess.check_output(args,text=True).strip()
run('mount','--make-rprivate','/')
with tempfile.TemporaryDirectory(prefix='native-ext4-growth-016-') as tmp:
    root=pathlib.Path(tmp);image=root/'data.ext4';target=root/'mount';target.mkdir()
    with image.open('xb') as f:f.truncate(128*1024*1024)
    run('mke2fs','-q','-F','-t','ext4','-b','4096',str(image))
    with image.open('r+b') as f:f.truncate(512*1024*1024)
    loop=run('losetup','--find','--show',str(image));mounted=False
    try:
        run('mount','-t','ext4',loop,str(target));mounted=True
        before=os.statvfs(target);fd=os.open(target,os.O_RDONLY|os.O_DIRECTORY)
        try:fcntl.ioctl(fd,0x40086610,struct.pack('Q',512*1024*1024//4096))
        finally:os.close(fd)
        after=os.statvfs(target)
        assert before.f_blocks*before.f_frsize<128*1024*1024
        assert after.f_blocks*after.f_frsize>450*1024*1024
        (target/'real-write').write_bytes(b'real ext4 data')
        assert (target/'real-write').read_bytes()==b'real ext4 data'
        print(json.dumps(dict(before_bytes=before.f_blocks*before.f_frsize,after_bytes=after.f_blocks*after.f_frsize,real_resize_ioctl=True)))
    finally:
        if mounted:run('umount',str(target))
        run('losetup','-d',loop)
'''
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','-u','root','--','unshare','--mount','--','python3','-'],input=payload,text=True,timeout=60).returncode)
