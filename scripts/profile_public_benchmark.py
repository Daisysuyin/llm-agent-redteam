"""Offline benchmark corpus profiler; reads only JSON or JSONL, never executes prompts.

Usage: python3 scripts/profile_public_benchmark.py path/to/file.json [more-files.jsonl]
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def load_records(path):
    path = Path(path)
    if path.suffix == ".jsonl":
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    elif path.suffix == ".json":
        records = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError("Only .json and .jsonl are supported")
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        raise ValueError("Expected a list of JSON objects")
    return records


def profile(path):
    path = Path(path)
    rows = load_records(path)
    counts = Counter(key for row in rows for key in row.keys())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "file": path.name,
        "sha256": digest,
        "record_count": len(rows),
        "field_coverage": {key: {"present": n, "fraction": n / len(rows) if rows else None}
                           for key, n in sorted(counts.items())},
        "note": "Dataset inspection only; no attacks or agent tools were executed.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="Previously downloaded JSON/JSONL corpus files")
    parser.add_argument("--out", help="Optional local JSON output")
    args = parser.parse_args()
    payload = {"files": [profile(path) for path in args.files]}
    result = json.dumps(payload, indent=2)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result + "\n")
    print(result)


if __name__ == "__main__":
    main()
