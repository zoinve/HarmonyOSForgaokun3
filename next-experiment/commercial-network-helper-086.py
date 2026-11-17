"""Preserve real networking; observe consolidated original thread-block logs."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
SOURCE = runpy.run_path(str(b / 'commercial-network-helper-085.py'))['SOURCE']
anchor = '"http", "https", "freeze"'
assert SOURCE.count(anchor) == 1
SOURCE = SOURCE.replace(anchor, anchor + ', "events"', 1)
EVENT = (b / 'commercial-event-reader-086.c').read_text()
anchor = 'static int run_mode(const char *mode)\n{'
assert SOURCE.count(anchor) == 1
SOURCE = SOURCE.replace(anchor, EVENT + '\n' + anchor + '\n    if(!strcmp(mode,"events"))return event086_read();', 1)
