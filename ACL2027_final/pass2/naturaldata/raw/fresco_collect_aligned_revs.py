# Copyright (c) Meta Platforms, Inc. and affiliates.

import argparse
import importlib
import json
import os
from typing import Dict, List, Optional, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry


# --- Map PIDs to their specific parsing function ---
PIDS = [
    "6", "35", "39", "54", "69", "102", "108", "127", "166", "276",
    "286", "451", "527", "551", "859", "1075", "1308", "1346", "1399",
    "2632", "6087",
]

PID_TO_PARSER_FN: Dict[str, Callable[[str], Optional[Tuple[Optional[str], Optional[str]]]]] = {}
for _pid in PIDS:
    _module = importlib.import_module(f"parse_infobox.p{_pid}")
    PID_TO_PARSER_FN[f"P{_pid}"] = _module.find_infobox_value_by_labels


# --- Constants ---
USER_AGENT = "MyResearchBot/1.0 (contact: your-email@example.com)" # Please update your email


# ==============================
# Requests session
# ==============================
def create_requests_session() -> requests.Session:
    """Creates a robust requests.Session with connection pooling and automatic retries."""
    session = requests.Session()
    retries = Retry(
        total=5, backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True,
        allowed_methods=frozenset(["GET", "POST"]),
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=128, pool_maxsize=128)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": USER_AGENT})
    return session
REQUESTS_SESSION = create_requests_session()


def process_single_entity(pid: str, input_file_path: str, output_file_path: str, wikitext_dir: str) -> int:
    """
    Processes a single entity file (Q*.json). It checks for alignment of the
    latest statement and saves the processed data if aligned.
    Returns 1 if a file was processed and saved, 0 otherwise.
    """
    if os.path.exists(output_file_path):
        return 0 # Skip if already processed

    parser_fn = PID_TO_PARSER_FN[pid]

    with open(input_file_path, "r") as f:
        entity = json.load(f)

    statements = entity.get("statements")
    if not statements:
        return 0

    parse_cache: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    processed_statements: List[Dict] = []
    is_latest_aligned = False

    for i, stmt in enumerate(reversed(statements)):
        is_latest_stmt = (i == 0)

        if is_latest_stmt:
            obj_labels = stmt.get("obj_label", [])
            obj_aliases = stmt.get("obj_aliases", [])
            valid_names = set(obj_labels) | set(obj_aliases)
            normalized_valid_names = {name.strip().lower() for name in valid_names if name}

        processed_revs: List[Dict] = []
        for rev in stmt.get("revisions", []):
            revid, link = rev.get("revid"), rev.get("link")
            if not link or not revid:
                continue

            if revid not in parse_cache:
                try:
                    parsed_value, wikitext = parser_fn(link)
                    parse_cache[revid] = (parsed_value, wikitext)
                    if wikitext:
                        wikitext_path = os.path.join(wikitext_dir, f"{revid}.txt")
                        with open(wikitext_path, "w", encoding="utf-8") as f_wiki:
                            f_wiki.write(wikitext)
                except Exception:
                    parse_cache[revid] = (None, None)

            parsed_value, _ = parse_cache[revid]

            new_rev = rev.copy()
            new_rev['parsed_value'] = parsed_value
            processed_revs.append(new_rev)

            if is_latest_stmt and not is_latest_aligned and parsed_value and normalized_valid_names:
                cleaned_parsed_value = parsed_value.strip().lower()
                if any(name in cleaned_parsed_value for name in normalized_valid_names):
                    is_latest_aligned = True

        new_stmt = stmt.copy()
        new_stmt['revisions'] = processed_revs
        processed_statements.append(new_stmt)

    if not is_latest_aligned:
        return 0 # Fail-fast: skip this entity if the latest statement did not align

    processed_statements.reverse()

    output_data = {
        "sub_qid": entity.get("sub_qid"),
        "sub_label": entity.get("sub_label"),
        "statements": processed_statements
    }

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, "w") as f_out:
        json.dump(output_data, f_out, indent=2)

    return 1


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(description="Fetch and validate Wikipedia revisions for Wikidata statements.")
    parser.add_argument("--input_dir", type=str, default="./data/collect_stats_with_revs")
    parser.add_argument("--output_dir", type=str, default="./data/collect_aligned_revs")
    parser.add_argument("--wikitext_output_dir", type=str, default="./data/wikitext")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers.")
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """Main execution function."""
    tasks: List[Tuple[str, str, str, str]] = []
    pids_to_process = sorted(list(PID_TO_PARSER_FN.keys()))
    print(f"Configured to process PIDs: {pids_to_process}")

    # --- Create a master list of all individual entity files to process ---
    for pid in pids_to_process:
        input_pid_dir = os.path.join(args.input_dir, pid)
        output_pid_dir = os.path.join(args.output_dir, pid)
        if not os.path.isdir(input_pid_dir):
            print(f"[INFO] No input directory found for PID {pid} at {input_pid_dir}. Skipping.")
            continue
        os.makedirs(args.wikitext_output_dir, exist_ok=True)

        for filename in os.listdir(input_pid_dir):
            if filename.startswith("Q") and filename.endswith(".json"):
                input_file_path = os.path.join(input_pid_dir, filename)
                output_file_path = os.path.join(output_pid_dir, filename)
                tasks.append((pid, input_file_path, output_file_path, args.wikitext_output_dir))

    if not tasks:
        print("No entity files found to process. Exiting.")
        return

    print(f"Found {len(tasks)} total entity files to process across {len(pids_to_process)} PIDs.")
    print(f"Wikitext will be saved in: {args.wikitext_output_dir}")

    total_processed = 0
    if args.workers <= 1:
        print("Running in sequential mode.")
        for task in tqdm(tasks, desc="Processing Entities"):
            total_processed += process_single_entity(*task)
    else:
        print(f"Running in parallel mode with {args.workers} workers.")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_task = {executor.submit(process_single_entity, *task): task for task in tasks}

            for future in tqdm(as_completed(future_to_task), total=len(tasks), desc="Processing Entities"):
                try:
                    result = future.result()
                    total_processed += result
                except Exception as exc:
                    task_info = future_to_task[future]
                    print(f"\n[ERROR] Task {task_info[0]}/{os.path.basename(task_info[1])} generated an exception: {exc}")

    print(f"\nProcessing complete. Newly processed and saved {total_processed} aligned entities.")


if __name__ == "__main__":
    main(parse_args())
