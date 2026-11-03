"""Generate an editable, local-only human review template from an evaluation report."""
import argparse
import json
from pathlib import Path


def make_template(report):
    entries = report.get("results")
    if not isinstance(entries, list):
        raise ValueError("Evaluation report must have a results list")
    return {
        "schema_version": "1",
        "instructions": "Fill only after human inspection. Never interpret automatic review flags as confirmed vulnerabilities.",
        "reviews": [{
            "id": entry["id"],
            "kind": entry["kind"],
            "review_status": "pending",
            "task_completion": "uncertain",
            "instruction_boundary": "uncertain",
            "answer_contamination": "uncertain",
            "reviewer_note": "",
        } for entry in entries],
    }


def main():
    parser = argparse.ArgumentParser(description="Create manual annotation template")
    parser.add_argument("--report", default="reports/eval_v2.json")
    parser.add_argument("--out", default="reports/review_template.json")
    args = parser.parse_args()
    source, dest = Path(args.report), Path(args.out)
    result = make_template(json.loads(source.read_text()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        parser.error("Output already exists; refusing to overwrite human annotations")
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Created {len(result['reviews'])} pending reviews at {dest}")


if __name__ == "__main__":
    main()
