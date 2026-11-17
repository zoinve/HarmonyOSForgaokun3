"""Extract readable text as an aid, never as desktop or interaction proof."""
from pathlib import Path
import csv
import hashlib
import io
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    report = ROOT / 'reports/commercial61-native-088'
    output = report / 'frame-text-observation'
    assert not output.exists()
    version = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, check=True).stdout
    records = []
    for moment, parent in ((120, 'full-frame'), (140, 'second-full-frame')):
        image = report / parent / 'source.png'
        result = subprocess.run(['tesseract', str(image), 'stdout', '-l', 'chi_sim+eng', '--psm', '11', 'tsv'],
                                capture_output=True, check=True, timeout=60)
        rows = list(csv.DictReader(io.StringIO(result.stdout.decode('utf-8')), delimiter='\t'))
        words = []
        for row in rows:
            text = row.get('text', '').strip()
            if not text or float(row['conf']) < 20:
                continue
            words.append(dict(text=text, confidence=float(row['conf']),
                              bounds=[int(row[key]) for key in ('left', 'top', 'width', 'height')]))
        records.append(dict(moment=moment, image=str(image.relative_to(report)),
                            image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                            tsv=result.stdout, stderr=result.stderr.decode('utf-8', errors='replace'), words=words))
    output.mkdir()
    for record in records:
        (output / (str(record['moment']) + '.tsv')).open('xb').write(record.pop('tsv'))
    value = dict(tool_version=version, frames=records, direct_visual_inspection=False,
                 ocr_is_not_desktop_or_interaction_proof=True)
    (output / 'result.json').open('x').write(json.dumps(value, indent=2, ensure_ascii=True))
    print(json.dumps(value, indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
