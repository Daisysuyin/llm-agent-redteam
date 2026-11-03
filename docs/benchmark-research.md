# Research-backed benchmark roadmap (November 2026)

This document distinguishes **academic benchmark scenarios**, **responsibly disclosed proof-of-concept cases**, and **observed in-the-wild attacks**. They are not interchangeable. Research code must use only local fake accounts, no genuine credentials or production services.

## Prioritized external sources

| Source | Original publication / repository | Published scope | Use in this project | License considerations |
| --- | --- | --- | --- | --- |
| InjecAgent (Zhan et al., 2024) | [Paper](https://arxiv.org/abs/2403.02691), [code](https://github.com/uiuc-kang-lab/InjecAgent) | 1,054 original attack/test cases, 17 user tools and 62 attacker tools | First choice for tool-response corpus inspection; later build a **sandboxed action-evaluation** adapter | Repository marked MIT; check embedded materials and attribution |
| BIPIA (Yi et al., 2023/2024) | [Repository](https://github.com/microsoft/BIPIA), [paper](https://arxiv.org/abs/2312.14197) | Five tasks: Web QA, Email QA, Table QA, Summarization, Code QA (upstream archived Sep 16, 2026) | First choice for document/email/QA indirect injection | Code is MIT; certain included datasets (e.g. WikiTableQuestions and Stack Exchange) use CC BY-SA 4.0. Check dataset-specific terms; upstream repository was archived Sep 16, 2026 |
| AgentDojo (Debenedetti et al., NeurIPS 2024) | [Paper](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html), [code](https://github.com/ethz-spylab/agentdojo) | Initial paper: 97 user tasks and 629 security test cases across realistic tool environments | Best long-term end-to-end sandbox: state transitions, genuine task success versus targeted attacker success | MIT repo; version-pin benchmark because versions evolve |
| Agent Security Bench (ASB, ICLR 2025) | [Paper](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5750f91d8fb9d5c02bd8ad2c3b44456b-Abstract-Conference.html), [code](https://github.com/agiresearch/ASB) | 10 scenarios, over 400 tools, 27 attack/defense method types, seven metrics | Compare defenses and utility/security trade-offs in later phase | Read repository license and per-dataset terms before reuse |
| CyberSecEval 2 (Meta, 2024) | [Paper](https://ai.meta.com/research/publications/cyberseceval-2-a-wide-ranging-cybersecurity-evaluation-suite-for-large-language-models/), [repo](https://github.com/facebookresearch/PurpleLlama) | Prompt injection + false refusal measurements among multiple security evaluations | Add false-refusal measurement and standard evaluation baselines | Verify dataset-specific conditions and model acceptable-use terms |
| HackAPrompt (Schulhoff et al., EMNLP 2023) | [Paper](https://aclanthology.org/2023.emnlp-main.302/), [dataset description](https://paper.hackaprompt.com/) | 600,000+ competition submissions and playground prompts | Optional attack-language diversity and taxonomy study | Primarily direct prompt hacking/jailbreak context, not an agent tool-call benchmark |

Counts are sourced from original **publication** descriptions and are not guarantees about current release sizes, deduplication, or benchmark run counts.

## Directly inspectable InjecAgent source files

The upstream repo currently documents:

- `data/user_cases.jsonl` — user instruction, user tool, expected tool parameters, and a tool-response template.
- `data/attacker_cases_dh.jsonl` — attack instruction, attacker tool and direct-harm goal.
- `data/attacker_cases_ds.jsonl` — data-theft attack descriptions.
- `data/test_cases_dh_base.json` — 510 paired cases under base attack setting.
- `data/test_cases_ds_base.json` — 544 paired cases under base attack setting.
- `data/test_cases_dh_enhanced.json` / `data/test_cases_ds_enhanced.json` — alternate enhanced versions of the **same** scenario sets.

**Do not combine base and enhanced variants as 2,108 independent attacks.** They reflect 1,054 base scenario combinations with alternate prompting. Source: [InjecAgent README](https://github.com/uiuc-kang-lab/InjecAgent#dataset).

Example source format from `user_cases.jsonl` (field names only): `User Tool`, `User Instruction`, `Tool Parameters`, `Tool Response Template`, `Thought`, `Level`. This is a *benchmark fixture*, not evidence of incidents on those service platforms.

## What we should actually measure

1. **Legitimate user task success (benign):** did authorized actions reach expected *sandbox state*?
2. **Legitimate user task success (under attack):** did the original task still succeed?
3. **Targeted attacker success:** was the **specific** unauthorized sandbox state reached?
4. **Unauthorized action rate:** did the tool trace contain forbidden calls, even if attack objective ultimately failed?
5. **Refusal and false-refusal rate:** did the model reject legitimate tasks?
6. **Detection precision, recall and false-positive rate:** these measure an independent **detector**, not end-to-end agent compromise.
7. **Judge reliability:** human-labeled agreement and uncertainty; do not infer security failure from benign descriptions of attack strings.

For each result log: model identifier and digest, seed, temperature, tool list, dataset version/commit, prompt and output, action trace, evaluator version, and approval policy. Avoid publication of raw private data.

## Specific, grounded milestones

**M1 — offline public-corpus profiling**: download InjecAgent base fixtures locally, record checksums, count records and field consistency. The included `scripts/profile_public_benchmark.py` runs offline, never evaluates a payload.

**M2 — BIPIA adaptation**: implement a *licensed* document/QA importer, preserve authorized task and the external-content insertion position. No downstream ASR comparability until scoring and evaluation method match.

**M3 — agent sandbox**: local fake mail, fake files and fake GitHub repos. Separate observations from mutating actions; deny cross-repository transfer by default. Deterministic policy checks in a tool gateway.

**M4 — real-model matrix**: compare at least two model sizes under a pinned Ollama setup; include benign runs, repeats and manual reviews. Publish distributions and caveats, not only aggregate ASR.

**M5 — reproducible report**: compare unauthorized action, task utility and reviewer disagreement; cite each upstream source.

## External source integrity

- Never import downloaded attacks as Python code or execute shell commands from dataset strings.
- Never pass a public benchmark attack directly to real GitHub, email, banking, smart-lock or financial tools.
- Keep raw third-party datasets outside version control, preserve attribution and verify terms before redistribution.
- The use of a corpus for **static detector testing** is distinct from running the official **end-to-end agent benchmark**.
