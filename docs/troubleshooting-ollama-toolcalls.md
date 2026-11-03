# Troubleshooting: 0 valid Ollama function-call responses

If a run reports `valid_responses: 0`, `errors: 10`, and `attacker_tool_attempt_rate: null`, **no attack success / defense conclusion is possible**.

## Root cause investigated

InjecAgent upstream stores `Tool Parameters` as a Python-style dictionary string, e.g. `"{'product_id': 'B08KFQ9HK5'}"`. Our first adapter placed this string directly inside a synthetic previous assistant `tool_calls[].function.arguments`, although Ollama expects **an object**. This can cause HTTP 400 for every test before inference. The revised adapter uses `ast.literal_eval` (never `eval`) and verifies the result is a dictionary. The CLI now prints the first three error messages and captures Ollama HTTP error details.

This is a likely structural issue based on code and sample schema; an actual user rerun is required to confirm it was the cause of every HTTP failure.

## Retry one case before ten

```bash
git fetch origin
git switch fix/ollama-injecagent-zero-valid-responses
python3 -m unittest discover -s tests -v
python3 -m redteam.injecagent \
  --dataset external_data/injecagent/test_cases_dh_base.json \
  --tools external_data/injecagent/tools.json \
  --model llama3.2:3b \
  --limit 1 --out reports/injecagent_dh_debug1.json
```

For prior runs, inspect errors:

```bash
python3 -c 'import json; r=json.load(open("reports/injecagent_dh_first10.json")); print(json.dumps(r["errors"][:3],indent=2))'
```

If the one-case smoke test succeeds, rerun `--limit 10`. If it fails, paste the printed first error *without private data*. Another possible model-specific failure is unavailable native tool-call support or schema validation. If a given local model lacks tool calling, selecting a different Ollama model is preferable to pretending textual responses are function calls.

The runner still executes **zero tools** and scores attempted attacker tools only, not real-world harm or official benchmark ASR.
