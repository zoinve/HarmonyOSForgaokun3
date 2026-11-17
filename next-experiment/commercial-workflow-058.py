from pathlib import Path

source = Path(__file__).with_name('commercial-workflow-054.py').read_text().replace('054', '058')
source = source.replace("'processing_specs_audited',", "'processing_specs_audited', 'eighth_register_x9_tested',")
source = source.replace('hwbreak-test.json', 'hwbreak-test-revision2.json')
source = source.replace('        for key in [', "        audit = json.loads((b.parent / 'reports/commercial-render-audit-058/result.json').read_text())\n        assert test['processing_specifications'] == audit['probes'], 'Exact audited test metadata required'\n        for key in [", 1)
exec(compile(source, __file__, 'exec'), globals())
