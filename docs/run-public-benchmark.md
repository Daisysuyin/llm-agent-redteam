# First hands-on public benchmark: InjecAgent (offline import)

The original InjecAgent evaluation benchmark includes user/attacker pairings and actual tool-call targets. This first milestone **only inspects the released data locally**. It does *not* report official agent Attack Success Rate.

## Download (from repository root, explicit manual opt-in)

```bash
mkdir -p external_data/injecagent
curl -fL --retry 2 https://raw.githubusercontent.com/uiuc-kang-lab/InjecAgent/main/data/user_cases.jsonl -o external_data/injecagent/user_cases.jsonl
curl -fL --retry 2 https://raw.githubusercontent.com/uiuc-kang-lab/InjecAgent/main/data/attacker_cases_dh.jsonl -o external_data/injecagent/attacker_cases_dh.jsonl
curl -fL --retry 2 https://raw.githubusercontent.com/uiuc-kang-lab/InjecAgent/main/data/test_cases_dh_base.json -o external_data/injecagent/test_cases_dh_base.json
curl -fL --retry 2 https://raw.githubusercontent.com/uiuc-kang-lab/InjecAgent/main/data/test_cases_ds_base.json -o external_data/injecagent/test_cases_ds_base.json

python3 scripts/profile_public_benchmark.py \
  external_data/injecagent/user_cases.jsonl \
  external_data/injecagent/attacker_cases_dh.jsonl \
  external_data/injecagent/test_cases_dh_base.json \
  external_data/injecagent/test_cases_ds_base.json \
  --out reports/injecagent_profile.json

python3 -m unittest discover -s tests -v
```

Expected base case totals from the upstream repository documentation: **510 direct-harm + 544 data-theft = 1,054**. The profile reports actual counts, field coverage and SHA-256 digests; use those observed counts in analysis rather than assuming them.

The original repo provides both base and enhanced attack versions, representing alternate prompting of the same paired tests. Their counts should not be interpreted as independent unique cases.

No input prompts are printed by default because arbitrary external records may contain manipulative or inappropriate instructions. The profiler neither evaluates payloads nor invokes Ollama.

## Important: before end-to-end model testing

The `Tool Response` and `User Instruction` fields may be inspected, but reproducing InjecAgent requires preserving tool definitions, user task, attacker's targeted action, agent loop and goal-based scoring. Simply placing `Tool Response` in our existing summarizer and reporting `attack_success_rate` would **not** reproduce the academic benchmark.

Do not invoke real services, send messages, move money or access live accounts. A later PR will introduce a mock tool gateway with deny-by-default policy checks and deterministic state scoring.

## Data attribution

Zhan et al. (2024), *InjecAgent*, https://github.com/uiuc-kang-lab/InjecAgent (repository marked MIT). Review the upstream LICENSE and source licenses before distributing copied content. This repo should contain only code and links, not the full third-party corpus.
