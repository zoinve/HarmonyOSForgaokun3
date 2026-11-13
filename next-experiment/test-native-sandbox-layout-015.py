"""Reproduce SDK profile lookup at original service UID in a disposable chroot."""
import subprocess
payload=r'''
import os,tempfile,pathlib,json
with tempfile.TemporaryDirectory(prefix='native-layout-015-') as tmp:
    root=pathlib.Path(tmp);root.chmod(0o755)
    (root/'system/profile').mkdir(parents=True)
    (root/'system/profile/installs.json').write_text('{"systemability":[{"name":511}]}')
    def check():
        pid=os.fork()
        if pid==0:
            os.chroot(root);os.chdir('/');os.setgroups([]);os.setgid(5555);os.setuid(5555)
            try:
                value=json.loads(pathlib.Path('/usr/system/profile/installs.json').read_text())
                os._exit(0 if value['systemability'][0]['name']==511 else 2)
            except FileNotFoundError:os._exit(1)
        return os.waitstatus_to_exitcode(os.waitpid(pid,0)[1])
    before=check();assert before==1
    (root/'usr').mkdir();(root/'usr/system').symlink_to('/system')
    after=check();assert after==0
    print(json.dumps({'missing_sdk_alias_exit':before,'real_profile_alias_exit':after,'uid':5555,'fixture_only':True}))
'''
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','-u','root','--','python3','-'],input=payload,text=True,timeout=30).returncode)
