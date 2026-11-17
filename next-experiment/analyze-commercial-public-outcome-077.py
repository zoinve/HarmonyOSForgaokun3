from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'analyze-commercial-public-outcome-076.py').read_text().replace(
    "else '076'", "else '077'").replace("['075', '076']", "['075', '076', '077']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
