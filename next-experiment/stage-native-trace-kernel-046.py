from pathlib import Path

source = Path(__file__).with_name('stage-native-binder-kernel-045.py').read_text()
source = source.replace('native-binder-kernel-045', 'native-trace-kernel-046')
source = source.replace('native-original-graphics-045', 'native-original-graphics-046')
source = source.replace('original_tokens_uid_checks_unchanged', 'security_config_unchanged')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
