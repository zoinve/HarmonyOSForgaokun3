"""Analyze438 original-service and passive HCI evidence, not UI acceptance."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'analyze-bluetooth-346.py').read_text()
    source = source.replace('commercial61-native-341', 'commercial61-native-438')
    source = source.replace('bluetooth-analysis-346.json', 'bluetooth-analysis-445.json')
    marker = " output.open('x').write(json.dumps(result,indent=2)+'\\n')"
    assert source.count(marker) == 1
    source = source.replace(marker, ''' result.update(
   hci_classic_outcome_events=[fields(line) for line in phase.splitlines()
      if line.startswith('BT435_OUTCOME ')],
   hci_channel_summaries=[fields(line) for line in phase.splitlines()
      if line.startswith('BT435_SESSION ')],
   summary_absence_not_zero_packets=True,
   le_connection_security_outcomes_observed_by435=False,
   hci_success_not_original_service_or_ui_pairing_acceptance=True)
''' + marker)
    exec(compile(source, 'analyze-bluetooth-445.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'analyze-bluetooth-445.generated.py')))
