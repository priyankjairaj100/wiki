# Copyright (c) Meta Platforms, Inc. and affiliates.

import argparse

import calendar
import json
import os
import time
from concurrent.futures import as_completed, ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, NamedTuple, Optional, Set, Tuple
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry


WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"  # English Wikipedia
USER_AGENT = "MyResearchBot/1.0 (contact: cownow4425@gmail.com)"
API_BATCH_SIZE = 50
Precision = Literal["year", "month", "day"]


def create_requests_session() -> requests.Session:
    """Creates a robust requests.Session with connection pooling and automatic retries."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
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


class Interval(NamedTuple):
    start: datetime  # inclusive
    end: datetime  # exclusive


def floor_to_precision(ts: str) -> datetime:
    """For start bounds: floor to the minimum of its precision (inclusive)."""
    s = ts.lstrip("+")
    date_part, _time_part = (s.split("T") + ["00:00:00Z"])[:2]
    y, m, d = date_part.split("-")
    y = int(y)
    if m == "00" and d == "00":  # year
        return datetime(y, 1, 1, tzinfo=timezone.utc)
    if d == "00":  # month
        m = int(m)
        return datetime(y, m, 1, tzinfo=timezone.utc)
    # day
    return datetime(y, int(m), int(d), tzinfo=timezone.utc)


def next_unit_start(ts: str) -> datetime:
    """For end bounds: ceil to the start of the next precision unit (exclusive)."""
    s = ts.lstrip("+")
    date_part, _time_part = (s.split("T") + ["00:00:00Z"])[:2]
    y, m, d = date_part.split("-")
    y = int(y)
    if m == "00" and d == "00":  # year -> next Jan 1
        return datetime(y + 1, 1, 1, tzinfo=timezone.utc)
    if d == "00":  # month -> next month 1
        m = int(m)
        if m == 12:
            return datetime(y + 1, 1, 1, tzinfo=timezone.utc)
        return datetime(y, m + 1, 1, tzinfo=timezone.utc)
    # day -> next day 00:00
    m, d = int(m), int(d)
    last = calendar.monthrange(y, m)[1]
    if d == last:
        if m == 12:
            return datetime(y + 1, 1, 1, tzinfo=timezone.utc)
        return datetime(y, m + 1, 1, tzinfo=timezone.utc)
    return datetime(y, m, d + 1, tzinfo=timezone.utc)


def normalize_interval_halfopen(
    start_ts: str, end_ts: Optional[str], global_upper: str
) -> Optional[Interval]:
    """Normalize Wikidata timestamps to a half-open [start, end) interval."""
    try:
        start = floor_to_precision(start_ts)
        global_upper_dt = datetime.fromisoformat(global_upper.replace("Z", "+00:00"))
        if end_ts:
            end_candidate = next_unit_start(end_ts)
        else:
            end_candidate = global_upper_dt
        end = min(end_candidate, global_upper_dt)
        if start >= end:
            return None
        return Interval(start, end)
    except Exception:
        return None


def get_sitelinks_batch(qids: List[str]) -> Dict[str, Dict[str, Optional[str]]]:
    """
    return: { QID: {"title": str|None, "pageid": str|None} }
    """
    out: Dict[str, Dict[str, Optional[str]]] = {}
    if not qids:
        return out

    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": "|".join(qids),
        "props": "sitelinks",
        "sitefilter": "enwiki",
        "redirects": "yes",
    }
    try:
        r = REQUESTS_SESSION.get(WIKIDATA_API_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        entities = data.get("entities", {})
        redirects = {item["from"]: item["to"] for item in data.get("redirects", [])}

        for qid in qids:
            ent = entities.get(qid, {})
            title = ent.get("sitelinks", {}).get("enwiki", {}).get("title")
            out[qid] = {"title": title, "pageid": None}

        # apply Wikidata redirects
        for old, new in redirects.items():
            if new in entities:
                t = (
                    entities.get(new, {})
                    .get("sitelinks", {})
                    .get("enwiki", {})
                    .get("title")
                )
                if old in out:
                    out[old]["title"] = t or out[old]["title"]

        # Then resolve to pageids through Wikipedia API
        titles = [v["title"] for v in out.values() if v["title"]]
        if titles:
            # chunk to avoid URL length issues
            CHUNK = 50
            title_to_pid: Dict[str, str] = {}
            for i in range(0, len(titles), CHUNK):
                tchunk = titles[i : i + CHUNK]
                p = {
                    "action": "query",
                    "format": "json",
                    "prop": "info",
                    "titles": "|".join(tchunk),
                    "redirects": "1",
                    "inprop": "url",
                }
                rq = REQUESTS_SESSION.get(WIKIPEDIA_API_URL, params=p, timeout=30)
                rq.raise_for_status()
                qd = rq.json()
                query_data = qd.get("query", {})
                pages = query_data.get("pages", {})
                wp_redirects = {
                    r["from"]: r["to"] for r in query_data.get("redirects", [])
                }
                normalized_map = {
                    n["from"]: n["to"] for n in query_data.get("normalized", [])
                }
                for pid, pd in pages.items():
                    if int(pid) > 0:
                        title_to_pid[pd.get("title")] = pid

                # Assign pageid taking into account normalization and redirects
                for qid, v in out.items():
                    original_title = v.get("title")
                    if not original_title:
                        continue
                    current_title = normalized_map.get(original_title, original_title)
                    final_title = wp_redirects.get(current_title, current_title)
                    if final_title in title_to_pid:
                        v["pageid"] = title_to_pid[final_title]

    except requests.exceptions.RequestException as e:
        print(f"[WARN] sitelinks batch failed: {e}")
        for qid in qids:
            out.setdefault(qid, {"title": None, "pageid": None})
    return out


def _title_to_pageid(title: Optional[str]) -> Optional[str]:
    if not title:
        return None
    p = {
        "action": "query",
        "format": "json",
        "prop": "info",
        "titles": title,
        "redirects": "1",
    }
    try:
        rq = REQUESTS_SESSION.get(WIKIPEDIA_API_URL, params=p, timeout=20)
        rq.raise_for_status()
        pages = rq.json().get("query", {}).get("pages", {})
        for pid, pd in pages.items():
            if int(pid) > 0:
                return pid
    except requests.exceptions.RequestException:
        return None
    return None


def get_revisions_for_period_by_pageid(
    pageid: str, start_iso: str, end_iso: str
) -> List[Dict[str, Any]]:
    if not (pageid and start_iso and end_iso):
        return []

    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "pageids": pageid,
        "rvprop": "ids|timestamp",
        "rvlimit": "max",
        "rvdir": "newer",
        "rvstart": start_iso,
        "rvend": end_iso,
    }

    revs: List[Dict[str, Any]] = []
    while True:
        try:
            resp = REQUESTS_SESSION.get(WIKIPEDIA_API_URL, params=params, timeout=60)
            if resp.status_code == 429:
                time.sleep(2)
                continue
            resp.raise_for_status()
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for pid, pd in pages.items():
                page_title = pd.get("title")
                for rev in pd.get("revisions", []) or []:
                    revs.append(
                        {
                            "revid": rev["revid"],
                            "title": page_title,
                            "timestamp": rev["timestamp"],
                            "link": f"https://en.wikipedia.org/w/index.php?oldid={rev['revid']}",
                        }
                    )
            cont = data.get("continue")
            if cont:
                params.update(cont)
                time.sleep(0.01)  # a bit shorter to speed things up
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"[WARN] revisions fetch failed for pageid={pageid}: {e}")
            break

    seen: Set[int] = set()
    uniq: List[Dict[str, Any]] = []
    for r in revs:
        rid = r.get("revid")
        if rid not in seen:
            seen.add(rid)
            uniq.append(r)
    return uniq


def process_pid_file(
    input_path: str,
    output_dir_for_pid: str,
    pid: str,
    before_timestamp: str,
    min_num_stmts: int,
):
    """
    Processes a single PID JSON file, reads all its entities, processes each one,
    and saves the results individually as `pid/sub_qid.json`.
    """
    try:
        with open(input_path, "r") as f:
            entities = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] Could not read or parse {input_path}: {e}")
        return

    qids_to_process = [
        entity.get("sub_qid") for entity in entities if entity.get("sub_qid")
    ]
    print(f"[{pid}] Found {len(qids_to_process)} QIDs. Fetching Wikipedia titles...")

    sitelinks: Dict[str, Dict[str, Optional[str]]] = {}
    batches = [
        qids_to_process[i : i + API_BATCH_SIZE]
        for i in range(0, len(qids_to_process), API_BATCH_SIZE)
    ]
    for batch in tqdm(batches, desc=f"[{pid}] Fetching sitelinks"):
        sitelinks.update(get_sitelinks_batch(batch))

    saved_cnt = 0
    for entity in tqdm(entities, desc=f"[{pid}] Processing entities"):
        sub_qid = entity.get("sub_qid")
        info = sitelinks.get(sub_qid) or {}
        pageid = info.get("pageid")
        title = info.get("title")

        if not pageid and not title:
            continue

        statements = entity.get("statements", []) or []
        if not statements:
            continue

        # --- Start of logic for a single entity ---
        grouped_by_time: Dict[Tuple, Dict[str, Any]] = {}
        for stmt in statements:
            if stmt.get("is_interval"):
                key = ("interval", stmt.get("start_time"), stmt.get("end_time"))
            else:
                key = ("point", stmt.get("point_time"))

            if key in grouped_by_time:
                existing_stmt = grouped_by_time[key]
                existing_stmt["obj_qid"].append(stmt["obj_qid"])
                existing_stmt["obj_label"].append(stmt["obj_label"])
                existing_stmt["obj_aliases"].extend(stmt["obj_aliases"])
            else:
                new_stmt = stmt.copy()
                new_stmt["obj_qid"] = [new_stmt["obj_qid"]]
                new_stmt["obj_label"] = [new_stmt["obj_label"]]
                new_stmt["obj_aliases"] = list(new_stmt["obj_aliases"])
                grouped_by_time[key] = new_stmt

        for stmt in grouped_by_time.values():
            if len(stmt["obj_qid"]) > 1:
                stmt["obj_aliases"] = sorted(list(set(stmt["obj_aliases"])))

        processed_statements = list(grouped_by_time.values())
        processed_statements.sort(
            key=lambda s: s.get("start_time") or s.get("point_time")
        )

        unique_statements: List[Dict[str, Any]] = []
        seen_obj_qids: Set[str] = set()
        for stmt in reversed(processed_statements):
            obj_qids = stmt.get("obj_qid")
            if not isinstance(obj_qids, list):
                obj_qids = [obj_qids]
            has_new_qid = False
            for qid in obj_qids:
                if qid not in seen_obj_qids:
                    has_new_qid = True
                    seen_obj_qids.add(qid)
            if has_new_qid:
                unique_statements.insert(0, stmt)

        effective_pageid: Optional[str] = pageid
        if not effective_pageid and title:
            pid_fallback = _title_to_pageid(title)
            if pid_fallback:
                effective_pageid = pid_fallback
        if not effective_pageid:
            continue

        if len(unique_statements) < min_num_stmts:
            continue

        if (
            unique_statements[-1].get("is_interval")
            and len([s for s in unique_statements if s.get("end_time") is None]) > 1
        ):
            continue

        for i, stmt in enumerate(unique_statements):
            start_ts = stmt.get("start_time") or stmt.get("point_time")
            end_ts = stmt.get("end_time")

            if not stmt.get("is_interval") and (i + 1) < len(unique_statements):
                next_stmt = unique_statements[i + 1]
                end_ts = next_stmt.get("start_time") or next_stmt.get("point_time")

            interval = normalize_interval_halfopen(start_ts, end_ts, before_timestamp)
            if not interval:
                stmt["revisions"] = []
                continue

            start_iso = interval.start.isoformat().replace("+00:00", "Z")
            end_iso = interval.end.isoformat().replace("+00:00", "Z")

            revisions = get_revisions_for_period_by_pageid(
                effective_pageid, start_iso, end_iso
            )
            stmt["revisions"] = revisions

        statements_with_revs = [s for s in unique_statements if s.get("revisions")]
        if len(statements_with_revs) < min_num_stmts:
            continue

        latest_stmt = unique_statements[-1]
        if not latest_stmt.get("revisions", []):
            continue

        new_record = {
            "sub_qid": sub_qid,
            "sub_label": entity.get("sub_label"),
            "statements": unique_statements,
        }

        out_path = os.path.join(output_dir_for_pid, f"{sub_qid}.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(new_record, f, indent=4, ensure_ascii=False)
            saved_cnt += 1
        except Exception as e:
            print(f"[{pid}] [WARN] Failed to write {out_path}: {e}")
        # --- End of logic for a single entity ---

    print(
        f"[{pid}] [INFO] Saved {saved_cnt} individual entity files into {output_dir_for_pid}"
    )


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch Wikipedia revisions for current Wikidata statements."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="./data/collect_stmts/after=2020-01-01_before=2025-08-31_min=2",
        help="Directory containing input 'output.json' files from collect_stmts.py",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./data/collect_stats_with_revs",
        help="Directory to save the JSON files per entity as pid/sub_qid.json.",
    )
    parser.add_argument(
        "--before_timestamp",
        type=str,
        default="2025-08-31T23:59:59Z",
        help="Global end timestamp for open-ended intervals.",
    )
    parser.add_argument("--min_num_stmts", type=int, default=2)
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers to process PIDs.",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """Main execution function."""

    files_to_process: List[Tuple[str, str, str]] = []
    for root, _, files in os.walk(args.input_dir):
        if "output.json" in files:
            pid = os.path.basename(root)
            input_path = os.path.join(root, "output.json")
            output_dir_for_pid = os.path.join(args.output_dir, pid)
            files_to_process.append((input_path, output_dir_for_pid, pid))
    print(f"Found {len(files_to_process)} PID files to process.")

    if args.workers <= 1:
        print("Running in sequential mode.")
        for input_path, output_dir_for_pid, pid in files_to_process:
            print(f"\n--- Processing {input_path} ---")
            process_pid_file(
                input_path,
                output_dir_for_pid,
                pid,
                args.before_timestamp,
                args.min_num_stmts,
            )
    else:
        print(f"Running in parallel mode with {args.workers} workers.")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_pid = {
                executor.submit(
                    process_pid_file,
                    input_path,
                    output_dir_for_pid,
                    pid,
                    args.before_timestamp,
                    args.min_num_stmts,
                ): pid
                for input_path, output_dir_for_pid, pid in files_to_process
            }
            for future in tqdm(
                as_completed(future_to_pid),
                total=len(files_to_process),
                desc="Processing PIDs",
            ):
                pid = future_to_pid[future]
                try:
                    future.result()
                except Exception as exc:
                    print(f"\n[ERROR] PID {pid} generated an exception: {exc}")


if __name__ == "__main__":
    main(parse_args())
