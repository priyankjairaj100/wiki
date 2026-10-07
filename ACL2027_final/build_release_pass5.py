"""Run the final release builder. See --help for final manifest requirements."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent/'pass5/release/build_final_packages.py'), run_name='__main__')
