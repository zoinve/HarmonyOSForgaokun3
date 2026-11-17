from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-hwbreak-065.py').read_text().replace('065', '073')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
