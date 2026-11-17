from pathlib import Path

source = Path(__file__).with_name('commercial-hwbreak-054.py').read_text()
source = source.replace('commercial-render-audit-054', 'commercial-render-audit-060')
source = source.replace("['transaction_process', 'process_command', 'render', 'uni_render']",
                        "['surface_draw', 'canvas_draw', 'draw_children', 'draw_content']")
exec(compile(source, __file__, 'exec'), globals())
