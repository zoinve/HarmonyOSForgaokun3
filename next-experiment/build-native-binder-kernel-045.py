"""Build an independent diagnostic kernel, never alter 031 or Ubuntu's kernel."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('build-native-binder-kernel-031.py')))['payload']
source = source.replace("old=root/'baremetal-identity-profile-003'", "old=root/'native-binder-kernel-031'")
source = source.replace("work=root/'native-binder-kernel-031'", "work=root/'native-binder-kernel-045'")
source = source.replace("reports/native-binder-kernel-031'", "reports/native-binder-kernel-045'")
source = source.replace("next-experiment/native-binder-pid-031.py", "next-experiment/native-binder-oneway-045.py")
source = source.replace("new,header=p['repair'](c.read_text(),h.read_text());c.write_text(new);h.write_text(header)",
                        "new=p['repair'](c.read_text());c.write_text(new)")
source = source.replace('async_supported=True,', 'async_supported=True,oneway_sender_pid_from_held_authentic_pid=True,original_tokens_uid_checks_unchanged=True,')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
