# Copyright (c) Meta Platforms, Inc. and affiliates.

import argparse
import json
import random
import re
from concurrent.futures import as_completed, ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import requests
from tqdm import tqdm
from utils import extract_infoboxes_and_intro


random.seed(42)
FILTERED_PIDS = ["P6", "P39"]


def get_wikitext_from_revid(
    revid: str, wikitext_dir: Union[str, Path]
) -> Optional[str]:
    """
    Fetches the wikitext for a given revision ID by reading it from a local file.
    """
    wikitext_path = Path(wikitext_dir) / f"{revid}.txt"
    if not wikitext_path.exists():
        return None

    try:
        return wikitext_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading wikitext file {wikitext_path}: {e}")
        return None


def get_redirects_for_page(page_title: str) -> List[str]:
    """
    Fetches a list of all page titles that redirect to the given Wikipedia page.
    Includes a User-Agent header for API best practices.
    """
    WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "TvWikiRankPassageCollector/1.0 (contact: your_email@example.com)"
    }
    params = {
        "action": "query",
        "format": "json",
        "list": "backlinks",
        "bltitle": page_title,
        "blfilterredir": "redirects",
        "bllimit": "max",
    }
    try:
        with requests.Session() as session:
            session.headers.update(headers)
            response = session.get(url=WIKIPEDIA_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            backlinks = data.get("query", {}).get("backlinks", [])
            redirect_titles = [item["title"] for item in backlinks]
            return redirect_titles

    except requests.exceptions.RequestException as e:
        print(f"\n[Warning] Wikipedia API request failed for '{page_title}': {e}")
        return []


def _find_matching_bracket(text: str, start_pos: int) -> int:
    """Helper to find matching '}}' for a '{{', handling nesting and malformed templates."""
    if not text.startswith("{{", start_pos):
        return -1
    level = 1
    i = start_pos + 2
    while i < len(text) - 1:
        if text[i : i + 2] == "{{":
            level += 1
            i += 2
        elif text[i : i + 2] == "}}":
            level -= 1
            if level == 0:
                next_char_pos = i + 2
                while next_char_pos < len(text) and text[next_char_pos].isspace():
                    next_char_pos += 1

                if next_char_pos < len(text) and text[next_char_pos] == "|":
                    level += 1  # It's a false end, re-increment level and continue searching.
                else:
                    return i + 2  # This seems to be the true end.
            i += 2
        else:
            i += 1
    return -1


def _parse_intro(text: str) -> List[str]:
    """Parses the intro part: splits templates and text blocks separately."""
    passages = []
    current_pos = 0
    while current_pos < len(text):
        start_of_content = current_pos
        while start_of_content < len(text) and text[start_of_content].isspace():
            start_of_content += 1
        if start_of_content >= len(text):
            break
        current_pos = start_of_content

        if text.startswith("{{", current_pos):
            end_of_template = _find_matching_bracket(text, current_pos)
            if end_of_template != -1:
                passages.append(text[current_pos:end_of_template])
                current_pos = end_of_template
            else:
                passages.append(text[current_pos:])
                break
        else:
            next_template_pos = text.find("{{", current_pos)
            end_pos = next_template_pos if next_template_pos != -1 else len(text)
            passages.append(text[current_pos:end_pos])
            current_pos = end_pos

    return [p.strip() for p in passages if p.strip()]


def _parse_body_by_section(text: str) -> List[str]:
    """Parses the body part: splits into sections based on '##' headers."""
    if not text.strip():
        return []

    pattern = r"(\n##+ .*)"
    parts = re.split(pattern, text)

    passages = []
    # The first part from split is the first header itself, which might be attached to some text
    # or be empty if the body starts exactly with a header.
    # We start from index 1 to group header + content.
    for i in range(1, len(parts), 2):
        header = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        full_section = (header + content).strip()
        if full_section:
            passages.append(full_section)

    return passages


def split_wikitext_conditionally(text: str) -> List[str]:
    """
    Main controller for splitting. Uses different logic for intro vs. body.
    """
    first_header_match = re.search(r"\n##+ .*", text)

    if first_header_match:
        intro_end_index = first_header_match.start()
        intro_text = text[:intro_end_index]
        body_text = text[intro_end_index:]
    else:
        intro_text = text
        body_text = ""

    intro_passages = _parse_intro(intro_text)
    body_passages = _parse_body_by_section(body_text)

    return intro_passages + body_passages


def split_into_passages(text: str, chunk_unit: Union[str, int]) -> List[str]:
    """Splits text based on the specified chunk_unit."""
    if not text:
        return []

    if chunk_unit == "paragraph":
        return split_wikitext_conditionally(text)
    else:
        chunk_size = int(chunk_unit)
        words = text.split()
        return [
            " ".join(words[i : i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]


def is_aligned(text: str, valid_names: Set[str]) -> bool:
    """Checks if any of the valid names are present in the text (case-insensitive)."""
    cleaned_text = text.strip().lower()
    return any(name in cleaned_text for name in valid_names)


# ==============================
# Core Processing Logic
# ==============================


def process_single_entity(
    pid: str,
    input_file_path: Path,
    output_file_path: Path,
    wikitext_dir_path: Path,
    chunk_unit: Union[str, int],
    min_num_stmts: int,
) -> int:
    """
    Processes a single entity file to generate positive and negative passages.
    Returns 1 if successful, 0 otherwise.
    """
    with input_file_path.open("r", encoding="utf-8") as f:
        entity = json.load(f)

    statements = entity.get("statements")
    if not statements:
        return 0

    if len(statements) < min_num_stmts:
        return 0

    sub_qid = entity.get("sub_qid")
    sub_label = entity.get("sub_label")
    if sub_qid == sub_label:
        return 0

    latest_stmt = statements[-1]

    if not latest_stmt.get("is_interval"):
        return 0

    if latest_stmt.get("is_interval"):
        latest_end_time = latest_stmt.get("end_time")
        other_end_times = [
            s.get("end_time") for s in statements[:-1] if s.get("end_time")
        ]
        if latest_end_time is not None:
            return 0
        if any(s.get("end_time") is None for s in statements[:-1]):
            return 0

        if not (latest_end_time is None or latest_end_time > max(other_end_times)):
            return 0

    # --- Step 1: Identify ground truth from the latest statement ---
    obj_labels = latest_stmt.get("obj_label", [])
    obj_aliases = latest_stmt.get("obj_aliases", [])
    valid_names = set(obj_labels) | set(obj_aliases)

    # Fetch redirect names from Wikipedia for each canonical label and add them to the set of valid names.
    redirect_names = set()
    for label in obj_labels:
        # Call the new helper function to get redirect page titles
        redirects = get_redirects_for_page(label)
        for r_name in redirects:
            redirect_names.add(r_name)

    valid_names.update(redirect_names)

    normalized_valid_names = {name.strip().lower() for name in valid_names if name}

    if not normalized_valid_names:
        return 0

    # --- Step 2: Select one random positive document ---
    aligned_positive_revs = [
        rev
        for rev in latest_stmt.get("revisions", [])
        if rev.get("parsed_value")
        and is_aligned(rev["parsed_value"], normalized_valid_names)
        and (wikitext_dir_path / f"{rev['revid']}.txt").exists()
    ]

    if not aligned_positive_revs:
        return 0

    positive_rev = max(aligned_positive_revs, key=lambda r: r["timestamp"])
    positive_timestamp = positive_rev["timestamp"]

    # --- Step 3: Select one random negative document from each group ---
    previous_stmts = statements[:-1]
    negative_groups: Dict[str, List[Dict]] = {}
    for stmt in previous_stmts:
        if not stmt.get("is_interval"):
            continue

        for rev in stmt.get("revisions", []):
            if rev["timestamp"] >= positive_timestamp:
                continue
            parsed_val = rev.get("parsed_value")

            if (
                parsed_val
                and not is_aligned(parsed_val, normalized_valid_names)
                and (wikitext_dir_path / f"{rev['revid']}.txt").exists()
            ):
                negative_groups.setdefault(parsed_val, []).append(rev)

    selected_negative_revs = [
        random.choice(rev_list) for rev_list in negative_groups.values()
    ]

    if not selected_negative_revs:
        return 0

    # --- Step 4 & 5: Fetch wikitext, split into passages, and classify ---
    from wikiextractor.wikiextractor.extract import (
        Extractor,
        ignoreTag,
        resetIgnoredTags,
    )

    ignoreTag("a")
    extractor = Extractor(0, 0, "", "", [])
    positive_passages: List[Dict] = []
    negative_passages: List[Dict] = []

    # Process positive document
    positive_wikitext = get_wikitext_from_revid(
        positive_rev["revid"], wikitext_dir_path
    )
    if positive_wikitext:
        cleaned_positive_wikitext = extractor.clean_text(
            positive_wikitext, mark_headers=True, expand_templates=True, html_safe=True
        )
        resetIgnoredTags()
        cleaned_positive_wikitext_particular = extract_infoboxes_and_intro(
            cleaned_positive_wikitext
        )
        rest_of_wikitext = cleaned_positive_wikitext.replace(
            cleaned_positive_wikitext_particular, "", 1
        )

        # Process intro/infobox passages
        processed_chunks = set()
        for chunk in split_into_passages(
            cleaned_positive_wikitext_particular, chunk_unit
        ):
            if chunk and len(chunk.split()) >= 10 and chunk not in processed_chunks:
                pssg = {"text": chunk, **positive_rev}
                if is_aligned(chunk, normalized_valid_names):
                    positive_passages.append(pssg)
                processed_chunks.add(chunk)

        # Process rest of the document passages
        for chunk in split_into_passages(rest_of_wikitext, chunk_unit):
            if (
                chunk
                and len(chunk.split()) >= 10
                and chunk not in processed_chunks
                and not is_aligned(chunk, normalized_valid_names)
            ):
                pssg = {"text": chunk, **positive_rev}
                negative_passages.append(pssg)
                processed_chunks.add(chunk)

    if not positive_passages:
        return 0

    # Process negative documents
    for neg_rev in selected_negative_revs:
        negative_wikitext = get_wikitext_from_revid(neg_rev["revid"], wikitext_dir_path)
        if negative_wikitext:
            cleaned_negative_wikitext = extractor.clean_text(
                negative_wikitext,
                mark_headers=True,
                expand_templates=True,
                html_safe=True,
            )
            resetIgnoredTags()
            for chunk in split_into_passages(cleaned_negative_wikitext, chunk_unit):
                if (
                    chunk
                    and len(chunk.split()) >= 20
                    and not is_aligned(chunk, normalized_valid_names)
                ):
                    pssg = {"text": chunk, **neg_rev}
                    negative_passages.append(pssg)

    output_data = {
        "pid": pid,
        "sub_qid": sub_qid,
        "sub_label": sub_label,
        "obj_labels": obj_labels,
        "obj_aliases": obj_aliases,
        "valid_names": list(valid_names),
        "positive_passages": positive_passages,
        "negative_passages": negative_passages,
    }

    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    with output_file_path.open("w", encoding="utf-8") as f_out:
        json.dump(output_data, f_out, indent=2, ensure_ascii=False)

    return 1


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Collect passages from aligned revisions."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="./data/collect_aligned_revs",
        help="Directory containing the processed Q*.json files from the previous step.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./data/collect_pssgs",
        help="Directory to save the final JSONL files with passages.",
    )
    parser.add_argument("--chunk_unit", default="paragraph")
    parser.add_argument(
        "--wikitext_output_dir", type=str, default="./data/wikitext"
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="Number of parallel workers."
    )
    parser.add_argument("--min_num_sub_qids", type=int, default=10)
    parser.add_argument("--min_num_stmts", type=int, default=2)
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """Main execution function."""
    input_dir_path = Path(args.input_dir)
    output_dir_path = Path(args.output_dir) / f"chunk_{args.chunk_unit}"
    wikitext_dir_path = Path(args.wikitext_output_dir)

    pids_to_process: List[str] = []
    if input_dir_path.is_dir():
        for p_dir in input_dir_path.iterdir():
            if (
                p_dir.is_dir()
                and p_dir.name.startswith("P")
                and len(list(p_dir.glob("Q*.json"))) >= args.min_num_sub_qids
            ):
                pids_to_process.append(p_dir.name)

    print(f"Found PID directories to process: {pids_to_process}")

    chunk_unit = int(args.chunk_unit) if args.chunk_unit.isdigit() else args.chunk_unit

    tasks: List[Tuple[str, Path, Path, Path]] = []
    for pid in pids_to_process:
        if pid in FILTERED_PIDS:
            continue

        input_pid_dir = input_dir_path / pid
        output_pid_dir = output_dir_path / pid

        if not input_pid_dir.is_dir():
            continue

        for input_file in input_pid_dir.glob("Q*.json"):
            output_file = output_pid_dir / input_file.name
            tasks.append(
                (
                    pid,
                    input_file,
                    output_file,
                    wikitext_dir_path,
                    chunk_unit,
                    args.min_num_stmts,
                )
            )

    if not tasks:
        print("No entity files found to process. Exiting.")
        return

    print(f"Generated {len(tasks)} tasks to process.")

    total_processed = 0
    if args.workers <= 1:
        print("Running in sequential mode.")
        for task in tqdm(tasks, desc="Processing Entities"):
            result = process_single_entity(*task)
            if result:
                total_processed += result
    else:
        print(f"Running in parallel mode with {args.workers} workers.")
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_task = {
                executor.submit(process_single_entity, *task): task for task in tasks
            }
            progress_bar = tqdm(
                as_completed(future_to_task),
                total=len(tasks),
                desc="Processing Entities (Parallel)",
            )

            for future in progress_bar:
                task_info = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        total_processed += result
                except Exception as exc:
                    failed_filename = task_info[1].name
                    print(
                        f"\n[ERROR] An exception occurred while processing {failed_filename}: {exc}"
                    )

    print(
        f"\nProcessing complete. Successfully generated {total_processed} passage files."
    )


if __name__ == "__main__":
    main(parse_args())
