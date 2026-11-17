from pathlib import Path

source = Path(__file__).with_name('commercial-workflow-054.py').read_text().replace('054', '059')
source = source.replace('original_userland_byte_identical', 'original_userland_binaries_byte_identical')
source = source.replace("'processing_specs_audited',", "'processing_specs_audited', 'eighth_register_x9_tested', 'public_parameter_only_change_tested',")
source = source.replace('hwbreak-test.json', 'hwbreak-test-revision2.json')
admission = '''        audit = json.loads((b.parent / 'reports/commercial-render-audit-059/result.json').read_text())
        assert test['processing_specifications'] == audit['probes'], 'Exact audited test metadata required'
        for key in ['''
source = source.replace('        for key in [', admission, 1)
exec(compile(source, __file__, 'exec'), globals())
