from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = (b / 'commercial-hwbreak-054.py').read_text()
source = source.replace('commercial-render-audit-054', 'commercial-render-audit-057')
source = source.replace("['transaction_process', 'process_command', 'render', 'uni_render']",
                        "['screen_skip_reason', 'screen_initial_gate', 'screen_missing_params', 'screen_skip_result']")
namespace = {'__file__': __file__, '__name__': __name__}
exec(compile(source, __file__, 'exec'), namespace)
specifications = namespace['specifications']


def instrument(original):
    result = namespace['instrument'](original)
    changes = [('attr.sample_regs_user=0x7f;', 'attr.sample_regs_user=0x27f;'),
               ('registers[7]', 'registers[8]'), ('header.size!=96', 'header.size!=104'),
               (' x6=0x%llx\\n', ' x6=0x%llx x9=0x%llx\\n'),
               ('(unsigned long long)registers[6]);', '(unsigned long long)registers[6],(unsigned long long)registers[7]);')]
    for old, new in changes:
        assert result.count(old) == 1, old
        result = result.replace(old, new, 1)
    return result
