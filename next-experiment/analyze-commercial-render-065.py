from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-render-064.py').read_text().replace('064', '065')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
