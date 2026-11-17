from pathlib import Path

source = Path(__file__).with_name('commercial-hwbreak-057.py').read_text().replace('057', '059')
source = source.replace("['screen_skip_reason', 'screen_initial_gate', 'screen_missing_params', 'screen_skip_result']",
                        "['partial_mode_result', 'screen_request_frame', 'commit_layers', 'screen_node_skip_result']")
exec(compile(source, __file__, 'exec'), globals())
