"""Add one exact, redacted read-only command; retain the original SSH restrictions."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
SOURCE=(BASE/'live-debug-reader-156.c').read_text()
anchor='int main(int argc, char **argv)'
assert SOURCE.count(anchor)==1
SOURCE=SOURCE.replace(anchor,(BASE/'live-radio-status-551.h').read_text()+'\n'+anchor,1)
anchor='    if (!strcmp(command, "status")) return status();'
assert SOURCE.count(anchor)==1
SOURCE=SOURCE.replace(anchor,anchor+'\n    if (!strcmp(command, "radio-status")) return radio551_status();',1)
