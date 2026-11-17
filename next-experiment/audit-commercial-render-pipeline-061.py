"""Audit real original command handlers with NodeId register arguments."""
from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-trace-046.py').read_text()
source = source.replace('reports/commercial-trace-audit-046', 'reports/commercial-render-audit-061').replace('commercial046/', 'commercial061/')
start = source.index('METHODS = [')
end = source.index('\n]\n', start) + 3
methods = [
    ('base', 'attach_uni_surface', 'RootNodeCommandHelper::AttachToUniSurfaceNode(', 'root=%x1:u64 surface=%x2:u64', False),
    ('base', 'add_child', 'BaseNodeCommandHelper::AddChild(', 'parent=%x1:u64 child=%x2:u64 index=%x3:s32', False),
    ('base', 'update_recording', 'RSCanvasNodeCommandHelper::UpdateRecording(', 'node=%x1:u64 type=%x3:u16', False),
    ('base', 'update_modifier_drawcmd', 'RSNodeCommandHelper::UpdateModifierNGDrawCmdList(', 'node=%x1:u64 modifier=%x3:u64', False),
]
source = source[:start] + 'METHODS = ' + repr(methods) + source[end:]
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
