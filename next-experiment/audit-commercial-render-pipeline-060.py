from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-060').replace('commercial046/', 'commercial060/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
methods = [
    ('service', 'surface_draw', 'DrawableV2::RSSurfaceRenderNodeDrawable::OnDraw(', '', False),
    ('service', 'canvas_draw', 'DrawableV2::RSCanvasRenderNodeDrawable::OnDraw(', '', False),
    ('base', 'draw_children', 'DrawableV2::RSRenderNodeDrawableAdapter::DrawChildren(', '', False),
    ('base', 'draw_content', 'DrawableV2::RSRenderNodeDrawableAdapter::DrawContent(', '', False),
]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
