#!/usr/bin/env python3
"""Run actual Qwen generations with a pinned, local llama.cpp server.

Input JSONL rows require an id and either prompt or messages. Optional system,
max_tokens, response_format, stop, and metadata fields are accepted. Outputs retain
the exact request and complete server response. No annotation field enters prompts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"
CACHE = Path(os.environ.get("ACL2027_INFERENCE_CACHE", str(ROOT.parents[2] / "acl2027_inference_cache")))
MODEL_SHA256 = "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"
MODEL_REVISION = "7dabda4d13d513e3e842b20f0d435c732f172cbe"
MODEL_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"


def json_request(url, payload=None, timeout=600):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data, {"Content-Type": "application/json"})
    # Local inference never traverses an environment HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as response:
        return json.load(response)


def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def make_request(row, max_tokens=128, seed=1729):
    if "messages" in row:
        messages = row["messages"]
    elif "prompt" in row:
        messages = []
        if row.get("system"):
            messages.append({"role": "system", "content": row["system"]})
        messages.append({"role": "user", "content": row["prompt"]})
    else:
        raise ValueError("Each row needs prompt or messages")
    request = {
        "model": MODEL_REPO,
        "messages": messages,
        "temperature": 0,
        "seed": seed,
        "max_tokens": row.get("max_tokens", max_tokens),
        "cache_prompt": False,
        "stream": False,
    }
    for key in ("response_format", "stop"):
        if key in row:
            request[key] = row[key]
    return request


class LocalRunner:
    """Context manager used by both the CLI and adaptive Python pipelines."""

    def __init__(self, *, log_path, model=None, server=None, threads=8, context=4096, batch=128, ubatch=64,
                 seed=1729, verify_model=True):
        self.model = Path(model or CACHE / MODEL_FILE).resolve()
        self.server = Path(server or CACHE / "llama-b11435" / "llama-server").resolve()
        self.threads, self.context, self.seed = threads, context, seed
        self.batch, self.ubatch = batch, ubatch
        self.log_path, self.verify_model = Path(log_path), verify_model
        self.process = self.log_file = None

    def __enter__(self):
        if self.verify_model and digest(self.model) != MODEL_SHA256:
            raise ValueError("Model checksum differs from the pinned official artifact")
        # Bind an ephemeral port first. The server and client run in one namespace.
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        self.url = f"http://127.0.0.1:{self.port}"
        self.command = [str(self.server), "-m", str(self.model), "--host", "127.0.0.1",
                        "--port", str(self.port), "-c", str(self.context),
                        "-t", str(self.threads), "-tb", str(self.threads), "--parallel", "1",
                        "-b", str(self.batch), "-ub", str(self.ubatch),
                        "--no-ui", "--seed", str(self.seed), "--temp", "0", "--n-gpu-layers", "0"]
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_path.open("w")
        self.started = time.perf_counter()
        self.process = subprocess.Popen(self.command, stdout=self.log_file, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.close()
                raise RuntimeError(f"Server exited; see {self.log_path}")
            try:
                health = json_request(self.url + "/health", timeout=1)
                if health.get("status") == "ok":
                    self.load_seconds = time.perf_counter() - self.started
                    self.properties = json_request(self.url + "/props", timeout=10)
                    return self
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(.2)
        self.close()
        raise TimeoutError(f"Server startup exceeded 180 seconds; see {self.log_path}")

    def generate(self, row, max_tokens=128):
        request = make_request(row, max_tokens=max_tokens, seed=self.seed)
        before = time.perf_counter()
        response = json_request(self.url + "/v1/chat/completions", request)
        elapsed = time.perf_counter() - before
        canonical = json.dumps(request, sort_keys=True, ensure_ascii=False).encode()
        return {
            "id": row["id"], "metadata": row.get("metadata", {}),
            "request": request, "request_sha256": hashlib.sha256(canonical).hexdigest(),
            "generation": response["choices"][0]["message"].get("content", ""),
            "finish_reason": response["choices"][0].get("finish_reason"),
            "response": response, "wall_seconds": elapsed,
            "model_repository": MODEL_REPO, "model_revision": MODEL_REVISION,
            "model_sha256": MODEL_SHA256, "runtime_release": "b11435",
        }

    def close(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        if self.log_file is not None:
            self.log_file.close()

    def __exit__(self, *exc):
        self.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--context", type=int, default=4096)
    parser.add_argument("--batch", type=int, default=128)
    parser.add_argument("--ubatch", type=int, default=64)
    parser.add_argument("--preflight-extra-input", type=Path, action="append", default=[])
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    rows = [json.loads(s) for s in args.input.read_text().splitlines() if s.strip()]
    ids = [str(row["id"]) for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Input ids must be unique")
    if args.output.exists() and not args.resume:
        raise FileExistsError("Output exists. Use a new path or --resume")
    completed = {}
    if args.resume and args.output.exists():
        for line in args.output.read_text().splitlines():
            result = json.loads(line)
            completed[str(result["id"])] = result
    for row in rows:
        old = completed.get(str(row["id"]))
        if old and old["request"] != make_request(row, args.max_tokens, args.seed):
            raise ValueError(f"Resume input changed for id {row['id']}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    log = args.output.with_suffix(".server.log")
    with LocalRunner(log_path=log, threads=args.threads, context=args.context, batch=args.batch, ubatch=args.ubatch, seed=args.seed) as runner:
        preflight_rows = list(rows)
        for extra_path in args.preflight_extra_input:
            preflight_rows.extend(json.loads(line) for line in extra_path.read_text().splitlines() if line.strip())
        token_counts = []
        for row in preflight_rows:
            request = make_request(row, args.max_tokens, args.seed)
            rendered = json_request(runner.url + "/apply-template", {"messages": request["messages"]})["prompt"]
            tokens = json_request(runner.url + "/tokenize", {"content": rendered, "add_special": True, "parse_special": True})["tokens"]
            reserved = len(tokens) + request["max_tokens"] + 16
            if reserved > args.context:
                raise ValueError(f"Prompt exceeds reserved context: {row['id']} {reserved}>{args.context}")
            token_counts.append({"id": row["id"], "prompt_tokens": len(tokens), "max_tokens": request["max_tokens"], "reserved_with_margin": reserved})
        token_preflight = {"requests": len(token_counts), "context_tokens": args.context, "margin_tokens": 16, "max_prompt_tokens": max(item["prompt_tokens"] for item in token_counts), "max_reserved_tokens": max(item["reserved_with_margin"] for item in token_counts), "all_fit": True, "counts": token_counts}
        args.output.with_suffix(".token_preflight.json").write_text(json.dumps(token_preflight, indent=2) + "\n")
        print(f"Token preflight: {len(token_counts)} prompts fit; largest reservation {token_preflight['max_reserved_tokens']}/{args.context}", flush=True)
        with args.output.open("a" if args.resume else "w") as f:
            for index, row in enumerate(rows):
                if str(row["id"]) in completed:
                    continue
                result = runner.generate(row, args.max_tokens)
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
                print(f"{index+1}/{len(rows)} id={row['id']} {result['wall_seconds']:.2f}s", flush=True)
        manifest = {"input_sha256": digest(args.input), "output_sha256": digest(args.output),
                    "server_command": runner.command, "server_properties": runner.properties,
                    "load_seconds": runner.load_seconds, "platform": platform.platform(),
                    "logical_cpus": os.cpu_count(), "seed": args.seed, "temperature": 0,
                    "cache_prompt": False, "rows": len(rows), "threads": args.threads, "context": args.context,
                    "batch": args.batch, "ubatch": args.ubatch,
                    "token_preflight_sha256": digest(args.output.with_suffix(".token_preflight.json"))}
    manifest["model_repository"] = MODEL_REPO
    manifest["model_revision"] = MODEL_REVISION
    manifest["model_sha256"] = MODEL_SHA256
    manifest["output_rows"] = sum(1 for line in args.output.open() if line.strip())
    manifest_path = args.output.with_suffix(".manifest.json")
    partial_path = manifest_path.with_suffix(".json.partial")
    with partial_path.open("w") as f:
        f.write(json.dumps(manifest, indent=2) + "\n")
        f.flush()
        os.fsync(f.fileno())
    partial_path.replace(manifest_path)


if __name__ == "__main__":
    main()
