"""Run the current revision package builder. Earlier entry points remain archived."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / 'pass6/release/build_final_packages.py'), run_name='__main__')
