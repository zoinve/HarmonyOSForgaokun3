from pathlib import Path

source = Path(__file__).with_name('commercial-hwbreak-054.py').read_text()
source = source.replace('commercial-render-audit-054', 'commercial-render-audit-061')
source = source.replace("['transaction_process', 'process_command', 'render', 'uni_render']",
                        "['attach_uni_surface', 'add_child', 'update_recording', 'update_modifier_drawcmd']")
exec(compile(source, __file__, 'exec'), globals())
