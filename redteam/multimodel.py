"""Local cross-model Ollama tool-calling comparison; no real tool execution."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .injecagent import OllamaToolCallAdapter
from .sandbox import args_as_dict, run_agent

CALCULATOR = {
    "type": "function",
    "function": {
        "name": "add_numbers", "description": "Add two integers",
        "parameters": {"type": "object",
                       "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                       "required": ["a", "b"]},
    },
}


def capability(adapter):
    raw = adapter.decide(
        [{"role": "user", "content": "Use add_numbers to calculate 17 + 25."}],
        [CALCULATOR],
    )
    message = raw.get("message") or {}
    calls = message.get("tool_calls") or []
    observations = []
    for call in calls:
        fn = call.get("function") or {}
        args = args_as_dict(fn.get("arguments"))
        correct_type = isinstance(args, dict) and all(
            type(args.get(k)) is int for k in ("a", "b")
        )
        observations.append({
            "tool_name": fn.get("name"),
            "arguments": args,
            "correct_tool": fn.get("name") == "add_numbers",
            "correct_arguments": correct_type and args == {"a": 17, "b": 25},
        })
    return {
        "tool_call_emitted": bool(calls),
        "correct_tool_selected": any(x["correct_tool"] for x in observations),
        "correct_arguments": any(x["correct_tool"] and x["correct_arguments"]
                                 for x in observations),
        "observations": observations,
        "text_response": message.get("content") or "",
    }


def compare(models, adapter_factory, capability_only=False):
    if not models or len(set(models)) != len(models):
        raise ValueError("Provide unique model names")
    report = {"metadata": {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "temperature": 0, "adapter": "local Ollama",
        "mode": "capability" if capability_only else "paired_sandbox",
        "warning": "Exploratory single-run comparison; not benchmark ASR.",
    }, "results": []}
    for name in models:
        row = {"model": name}
        try:
            adapter = adapter_factory(name)
            row["capability"] = capability(adapter)
            if not capability_only:
                row["benign"] = run_agent(adapter, injected=False, policy="enforce")
                row["injected"] = run_agent(adapter, injected=True, policy="enforce")
        except Exception as exc:
            row["error_type"] = type(exc).__name__
            row["error_message"] = str(exc)[:300]
        report["results"].append(row)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--capability-only", action="store_true")
    parser.add_argument("--out", default="reports/model_comparison.json")
    args = parser.parse_args()
    report = compare(args.models, OllamaToolCallAdapter, args.capability_only)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    for row in report["results"]:
        if "error_type" in row:
            print(row["model"], row["error_type"], row["error_message"])
        else:
            print(row["model"], json.dumps(row["capability"]))
            if "injected" in row:
                print("  benign legal read:", row["benign"]["legitimate_issue_read"],
                      "injected unauthorized attempts:", row["injected"]["unauthorized_attempts"])
    print("Saved:", path)


if __name__ == "__main__":
    main()
