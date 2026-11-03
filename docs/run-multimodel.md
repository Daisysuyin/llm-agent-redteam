# Multi-model capability and sandbox comparison

The existing single-run Llama 3.2 3B capability output showed a correct tool name but
`expected_call_emitted=false`; a subsequent raw request generated the correct
`add_numbers(a=17,b=25)` call. This discrepancy may be from nondeterministic generation
or scoring of different responses. The new harness **preserves the actual observed
arguments** and scores tool selection separately from argument accuracy.

## Run locally

```bash
cd ~/llm-agent-redteam
git fetch origin
git switch feature/multimodel-evaluation
python3 -m unittest discover -s tests -v
ollama pull qwen3:8b
python3 -m redteam.multimodel --models llama3.2:3b qwen3:8b \
  --capability-only --out reports/model_capability_comparison.json
python3 -m json.tool reports/model_capability_comparison.json
```

To include paired, completely in-memory sandbox scenarios:

```bash
python3 -m redteam.multimodel --models llama3.2:3b qwen3:8b \
  --out reports/model_sandbox_comparison.json
```

These runs use the same prompt, tool schema, temperature and sandbox policy for
both models. The calculator and fictional repository tools **never touch external
systems**. Model errors are recorded and must not count as security successes.

This remains an exploratory comparison (one run per model, synthetic scenarios).
Future work: repeated trials, pinned Ollama model digests, benign-task success
scoring and published benchmark goal evaluators.
