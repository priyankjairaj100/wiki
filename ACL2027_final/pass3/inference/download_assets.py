#!/usr/bin/env python3
"""Download immutable official model and runtime assets. Python standard library only."""
import hashlib
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent
ASSETS = [
    {
        "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/91cad51170dc346986eccefdc2dd33a9da36ead9/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "sha256": "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
    },
    {
        "filename": "llama-b11435-bin-ubuntu-x64.tar.gz",
        "url": "https://github.com/ggml-org/llama.cpp/releases/download/b11435/llama-b11435-bin-ubuntu-x64.tar.gz",
        "sha256": "ee617d7af304985e268fbc33bdd8fe44110f1dc2f599ecb27bdf08890e6e6e4c",
    },
]


def sha256(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def main():
    cache = ROOT / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    for spec in ASSETS:
        path = cache / spec["filename"]
        if path.exists() and sha256(path) == spec["sha256"]:
            print("Verified existing", path.name, flush=True)
            continue
        partial = path.with_suffix(path.suffix + ".partial")
        print("Downloading", path.name, flush=True)
        with urllib.request.urlopen(spec["url"], timeout=180) as src, partial.open("wb") as dst:
            while block := src.read(16 * 1024 * 1024):
                dst.write(block)
        if sha256(partial) != spec["sha256"]:
            raise ValueError(f"Checksum mismatch: {partial}")
        partial.replace(path)
    archive = cache / ASSETS[1]["filename"]
    with tarfile.open(archive) as tar:
        # Avoid rewriting a verified runtime while a local server is running.
        extracted = True
        for member in tar.getmembers():
            target = cache / member.name
            if member.isfile():
                if not target.is_file() or sha256(target) != hashlib.file_digest(tar.extractfile(member), "sha256").hexdigest():
                    extracted = False
                    break
            elif member.issym():
                if not target.is_symlink() or str(target.readlink()) != member.linkname:
                    extracted = False
                    break
        if extracted:
            print("Verified extracted runtime.", flush=True)
            return
        # The data filter rejects unsafe paths and suppresses archived ownership.
        tar.extractall(cache, filter="data")
    print("Assets verified and ready.", flush=True)


if __name__ == "__main__":
    main()
