from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-resource-outcome-070.py').read_text().replace(
    "baseline=observe('069'),candidate=observe('070')", "baseline=observe('070'),candidate=observe('072')").replace(
    'commercial61-native-070/resource-outcome-analysis.json', 'commercial61-native-072/resource-outcome-analysis.json')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
