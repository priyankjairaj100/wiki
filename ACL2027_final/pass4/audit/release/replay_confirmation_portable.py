#!/usr/bin/env python3
"""Run the original strict audit after resolving its recorded project prefix.

Only path resolution changes. The original manifests and audit source are never
edited. Every recorded input hash remains mandatory. No model assets are opened.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SENTINEL = "pass4/pipeline/run_matched.py"


def recorded_prefixes():
    prefixes = set()
    for track in ["human", "validation"]:
        record = json.loads((ROOT / f"pass4/pipeline/{track}/manifest.json").read_text())
        matches = [str(name)[:-len(SENTINEL)] for name in record["inputs"]
                   if Path(name).is_absolute() and str(name).endswith(SENTINEL)]
        if len(matches) != 1:
            raise RuntimeError("Expected one recorded project prefix in " + track)
        prefixes.add(matches[0])
    return prefixes


def main():
    path = ROOT / "pass4/protocol/audit_confirmation.py"
    spec = importlib.util.spec_from_file_location("pass4_confirmation_audit_original", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_sha = module.sha
    prefixes = recorded_prefixes()

    def portable_sha(path):
        text = str(path)
        if Path(path).is_absolute():
            # A copied project can itself be nested below the historical root.
            # Its current absolute paths must not receive the prefix twice.
            if Path(path).is_relative_to(ROOT):
                return original_sha(path)
            for prefix in prefixes:
                if text.startswith(prefix):
                    relative = Path(text[len(prefix):])
                    if relative.is_absolute() or ".." in relative.parts:
                        raise RuntimeError("Unsafe recorded path: " + text)
                    return original_sha(ROOT / relative)
        return original_sha(path)

    module.sha = portable_sha
    print("Historical project prefixes resolve to the current release root; all hashes remain mandatory.", flush=True)
    module.main()


if __name__ == "__main__":
    main()
