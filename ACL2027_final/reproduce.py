"""Run the current revision verifier. Earlier entry points remain archived."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().with_name('verify_revision.py')), run_name='__main__')
