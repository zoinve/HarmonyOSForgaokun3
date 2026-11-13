"""Restore lab preparation flags only after trial011 evidence verification."""
from pathlib import Path
source=Path(__file__).with_name('restore-baremetal-lab-workspace-rw-002.py').read_text()
source=source.replace('baremetal-native-trial-001-evidence-immediate','baremetal-native-trial-011-collected').replace('baremetal-lab-workspace-rw-002','baremetal-lab-workspace-rw-011').replace('len(files) == 20','len(files) == 340')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
