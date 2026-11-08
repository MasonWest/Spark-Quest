"""Compatibility entry: validate Shuffle standard guide and retained readings."""
from pathlib import Path
import runpy,sys
sys.argv=[str(Path(__file__).with_name('check-linked-readings.py')),'l5-what-is-shuffle']
runpy.run_path(sys.argv[0],run_name='__main__')
