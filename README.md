# LLM Agent Red Teaming & Defense Evaluation Framework

A reproducible, **offline teaching prototype** for direct prompt injection, indirect document injection, and tool-output injection.

## Quick start

Requires Python 3.10+; no external dependencies.

```bash
python -m redteam --mode both
python -m unittest discover -s tests -v
```

The runner generates local JSON reports under `reports/` (excluded from Git).

## Architecture

```text
Synthetic JSONL scenarios -> simulated agent -> baseline / guarded evaluation
                                            -> scoring -> JSON reports
```

The six educational scenarios model direct messages, retrieved-document injection, and tool-output injection. They attempt either to redirect a summarization task or to disclose a **fake** token. The baseline simulator intentionally follows suspicious instructions; the guarded simulator uses simple regular-expression detection.

## Repository structure

- `data/scenarios.jsonl` — synthetic test cases
- `redteam/__main__.py` — command-line evaluator, simulated agent and reporting
- `tests/test_harness.py` — five unit tests
- `.github/workflows/test.yml` — automated CI tests

## Important limitations

**This is not a benchmark on a real LLM.** All outputs and attack-success scores are deterministic simulations. The regex detector is intentionally simplistic and not robust to paraphrasing, encoding, benign false positives, or adaptive adversaries. No external LLM or Gray Swan Arena integration has been implemented.

## Development roadmap

1. Add an opt-in local or cloud model adapter with environment-based credentials.
2. Add benign controls and report false-positive and false-negative rates.
3. Introduce a sandboxed structured tool-calling agent and explicit trust-boundary enforcement.
4. Evaluate authorized live-model experiments with documented scoring.
5. Add visual reports and responsible-disclosure templates.

## Ethical use

Only test systems you own or have authorization to assess. Never store real secrets or private information in datasets, reports, or CI logs. Follow each testing platform's rules.

## Resume-ready description

Developed a Python evaluation harness for **synthetic** LLM-agent prompt-injection scenarios, comparing baseline and guarded behaviors through automated scoring and CI tests. Do not claim real-model attack performance until measured.
