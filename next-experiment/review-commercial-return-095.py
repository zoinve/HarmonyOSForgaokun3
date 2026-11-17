"""Preserve OCR and remaining native TEE failures after the completed 095 boot."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-095'
    out = folder/'post-return-review.json'
    assert not out.exists()
    manifest = json.loads((folder/'runtime-evidence/retrieval-manifest.json').read_text())
    raw = folder/'runtime-evidence/raw'
    def read(name):
        body = (raw/name).read_bytes()
        record = manifest['files'][name]
        assert len(body) == record['bytes'] and hashlib.sha256(body).hexdigest() == record['sha256']
        return body
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    parse = runpy.run_path(str(BASE/'native-ppm-evidence-068.py'))['parse_ppm']
    frames = {}
    pixels = []
    for tag, directory, number in (('before', 'full-frame', '068'), ('after', 'second-full-frame', '075')):
        path = folder/directory/'source.png'
        result = subprocess.run(['tesseract', str(path), 'stdout', '-l', 'chi_sim+eng'],
                                capture_output=True, timeout=30)
        assert result.returncode == 0, result.stderr
        body = read('full-source-'+number+'.ppm')
        width, height, rgb = parse(body)
        assert (width, height) == (2560, 1600)
        pixels.append(rgb)
        frames[tag] = dict(source_png_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           source_ppm_sha256=hashlib.sha256(body).hexdigest(),
                           ocr_text=sanitize(result.stdout), ocr_is_not_visual_desktop_proof=True)
    hilog = read('interactive-hilog030.log')
    failures = [sanitize(line) for line in hilog.splitlines() if b'DcmHdfService' in line and b'TEEC initial failed' in line]
    udid_errors = sum(b'GetDevUdidData' in line and b'Failed' in line for line in hilog.splitlines())
    result = dict(run=manifest['run'], frames=frames,
        changed_source_pixels=sum(pixels[0][i:i+3] != pixels[1][i:i+3] for i in range(0, len(pixels[0]), 3)),
        original_dcm_tee_initialization_failure_count=len(failures),
        original_dcm_tee_initialization_failures=failures,
        original_dcm_udid_failure_lines_in_recovered_hilog=udid_errors,
        original_udid_success_proven_by_separate_native_helper=True,
        image_inputs_rejected_by_viewer=True, desktop_success_proven=False, activation_success_proven=False)
    out.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
