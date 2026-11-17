from pathlib import Path

source = Path(__file__).with_name('test-commercial-hwbreak-054.py').read_text().replace('054', '056')
source = source.replace("['transaction_process', 'process_command', 'render', 'uni_render']",
                        "['screen_draw', 'screen_request_frame', 'commit_layers', 'worker_root_nonnull']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
