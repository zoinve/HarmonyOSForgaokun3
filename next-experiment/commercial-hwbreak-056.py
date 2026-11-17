from pathlib import Path

source = Path(__file__).with_name('commercial-hwbreak-054.py').read_text()
source = source.replace('commercial-render-audit-054', 'commercial-render-audit-056')
source = source.replace("['transaction_process', 'process_command', 'render', 'uni_render']",
                        "['screen_draw', 'screen_request_frame', 'commit_layers', 'worker_root_nonnull']")
exec(compile(source, __file__, 'exec'), globals())
