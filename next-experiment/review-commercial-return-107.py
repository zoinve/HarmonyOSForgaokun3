from pathlib import Path
import hashlib
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-107'
    output = folder / 'post-return-review.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    parse = runpy.run_path(str(ROOT / 'next-experiment/native-ppm-evidence-068.py'))['parse_ppm']
    images = [folder / name / 'source.png' for name in ('full-frame', 'second-full-frame')]
    texts = []
    pixels = []
    for path, number in zip(images, ('068', '075')):
        run = subprocess.run(['tesseract', str(path), 'stdout', '-l', 'chi_sim+eng', '--psm', '11'], capture_output=True, check=True, timeout=30)
        texts.append(dict(source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          text=run.stdout.decode('utf-8').strip()))
        name = 'full-source-' + number + '.ppm'
        data = (folder / 'runtime-evidence/raw' / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == manifest['files'][name]['sha256']
        width, height, rgb = parse(data)
        assert (width, height) == (2560, 1600)
        pixels.append(rgb)
    count = sum(pixels[0][i:i+3] != pixels[1][i:i+3] for i in range(0, len(pixels[0]), 3))
    result = dict(full_resolution=[2560, 1600], different_pixels=count, ocr=texts,
        visual_inspection_performed=False, viewer_input_rejected_in_this_environment=True,
        ocr_and_pixel_changes_are_not_desktop_proof=True, desktop_verified=False, interaction_verified=False)
    output.open('x').write(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))
