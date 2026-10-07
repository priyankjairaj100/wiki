#!/usr/bin/env python3
"""Run all CPU evidence checks without model calls or downloads."""
import argparse,os,pathlib,subprocess,sys
here=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--source',type=pathlib.Path,required=True,help='Original wikigraphrag-code-and-data directory')
ap.add_argument('--templama-source',type=pathlib.Path,required=True,help='Original test_with_aliases.json from TempLAMA')
args=ap.parse_args();env=dict(os.environ)
env['EVIDENCE_SOURCE']=str(args.source.resolve());env['TEMPLAMA_SOURCE']=str(args.templama_source.resolve())
for script in ['audit_release.py','run_evidence.py','run_sensitivity.py','run_prefix.py','audit_templama_source.py','score_source_sets.py','score_single_value_slice.py']:
 print(f'Running {script}',flush=True)
 subprocess.run([sys.executable,str(here/script)],env=env,check=True)
