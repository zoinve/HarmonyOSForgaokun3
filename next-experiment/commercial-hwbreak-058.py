from pathlib import Path

source = Path(__file__).with_name('commercial-hwbreak-057.py').read_text().replace('057', '058')
source = source.replace("['screen_skip_reason', 'screen_initial_gate', 'screen_missing_params', 'screen_skip_result']",
                        "['frame_skip_result', 'screen_node_skip_result', 'processor_create_failed', 'processor_init_failed']")
exec(compile(source, __file__, 'exec'), globals())
