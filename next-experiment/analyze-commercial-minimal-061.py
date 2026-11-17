from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-minimal-057.py').read_text().replace('057', '061')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
