# AutoPrompter hand-off (written 2026-10-05)

Read this first. It replaces re-reading the long session. Verify anything before relying on it (state may have moved).


## Update, end of 2026-10-05 (read this first in a cloud session)
- A cloud session sees only this repo. Paths below under `~/autoprompter-experiments/` and `~/.claude/` exist only on the user's phone (Termux). What was copied into the repo:
  - `notes/HANDOFF.md` (this file).
  - `notes/Prompt optimization datasets and systems.md`: research report comparing AutoPrompter with DSPy (MIPROv2, COPRO, Bootstrap, SIMBA), GEPA, TextGrad, ProTeGi, OPRO, APE, EvoPrompt, PromptAgent, PromptWizard, AdalFlow. Tables A/B + ranked fixes with evidence tiers.
  - `notes/research_notes/`: the 5 cited source notes behind the report.
  - `.claude/skills/autoprompter/`: the project skill (re-scanned and enhanced 2026-10-05; `references/experiments.md` has the run results and lessons).
- Verified in code (the report's key claims): failing examples' expected answers are shown to the Optimizer (`src/optimization_system.py:556`); every new prompt replaces the current one, no acceptance gate (`:853`); the "best" gate is a t-test with bootstrap fallback on TRAIN scores (`:432`); holdout plays no part in the loop.
- Ranked next fixes (from the report): 1) train/val/test split, accept a new prompt only if it beats the current one on val (AdalFlow/TextGrad/GEPA style); 2) stop showing expected answers to the Optimizer and reject prompts containing training labels; 3) exact match, refusals score 0; 4) val and test sets of 30-50+ items each; 5) several candidates per step (existing `generate_candidates`/`evaluate_candidates_parallel`).
- Status: user was offered to implement fix 1 on the fork; not started.

## Goal
The user wants to run AutoPrompter (autonomous prompt optimizer: Optimizer LLM rewrites a prompt, Target LLM answers a dataset, a metric scores it) with **Claude as the LLM** instead of OpenRouter or local models, keeping the existing backends. Then use it to optimize the `continuous-learning-v2` skill (`~/skills/continuous-learning-v2/SKILL.md`), Opus as Optimizer, Sonnet or Haiku as Target.

## Repo state (`/data/data/com.termux/files/home/AutoPrompter`, branch `main`)
- `55f4479` Adding claude_cli backend. `f5eda3c` Add reuse_dataset option (on top of upstream `b42dbbc`). Both pushed to `mine` (the fork) on 2026-10-05; nothing pushed to `origin`. This file and the research live on branch `handoff-docs`.
- Remotes: `origin` = maintainer `gauravvij/AutoPrompter`, fetch only (push URL set to `DISABLED` on purpose: the user does NOT want to push to the maintainer). `mine` = the user's fork `https://github.com/clumsy-cpu/AutoPrompter` (exists on GitHub). Pushing to `mine` is the user's call (`git push mine main`).
- Local git identity: `clumsy-cpu <gnbaly@gmail.com>`. `.claude/` is in `.git/info/exclude`.
- Leftover worktrees and branches were removed on 2026-10-05; only `main` remains. The `autoprompter` skill was re-scanned and enhanced the same day (old copy: `autoprompter-experiments/patches/SKILL.md.bak3`).
- Tests: `python3 -m pytest tests/test_reuse_dataset.py tests/test_claude_cli_client.py -q -p no:cacheprovider` gives 8 passed. The older tests (`test_integration.py`, `test_optimization_fixes.py`) have 10 failures that exist on untouched upstream too (hardcoded `/root/AutoPrompter/...` paths). Not caused by us.

## What was built
1. **`claude_cli` backend** (`src/claude_cli_client.py`, `ClaudeCLIConfig` and `_build_llm_config` in `src/config_manager.py`, `create_llm_client` in `src/optimization_system.py`, `config_claude.yaml`, README section).
   - Each call runs `claude -p --safe-mode --tools "" --no-session-persistence --output-format json --system-prompt <msg> --model <alias>` with the prompt on stdin. `--safe-mode` drops CLAUDE.md, hooks, skills and MCP but keeps the Claude Code login (`--bare` would need an API key). CLI output is a JSON array of events; the item with `"type":"result"` holds `result`, `is_error`, `usage`, `modelUsage`.
   - `backend: "claude_cli"`, `model` = alias (`opus`, `sonnet`, `haiku`) or full id. `temperature` and `max_tokens` are accepted and ignored. 3 retries.
2. **`experiment.reuse_dataset`** (default false). Upstream `run()` always called `generate_dataset(force_refresh=True)`, so a saved dataset was never used. Now `force_refresh=not reuse_dataset`. Use `-o experiment.reuse_dataset=true` (the `-o` parser casts true/false). With it, the first `batch_size` entries of `storage.dataset_file` are used, so set `batch_size` to the number of entries.
3. **Skill fixed**: `~/.claude/skills/autoprompter/SKILL.md` (corrected claims about dataset reuse, added metric gotchas and claude_cli notes). Backup of the pre-fix file: `autoprompter-experiments/patches/SKILL.md.bak2`; diff: `skill_fix.diff`.
4. User's global `~/.claude/CLAUDE.md` got two rules: "Diffs: always diff the entire file" and "Skill First: check for a repo's skill before searching".

## Environment facts (Termux)
- `scipy` is imported at the top of `src/optimization_system.py` but was missing from `requirements.txt` (added). `pip install scipy` does not build on Termux. Working fix: `pkg install python-scipy` (tur-packages, 1.18.1). `python2-scipy` is useless here.
- `flask` and `flask_cors` are needed only for `web_ui.py`. `OPENROUTER_API_KEY` is not set; not needed for claude_cli.
- `sentence-transformers` is not installed; the ledger falls back to exact-hash duplicate checks.

## Experiment results (all Claude via claude_cli)
| Run | Optimizer / Target | Task | Result |
|---|---|---|---|
| 1 | sonnet / haiku | default sentiment | 1.0 from the baseline (too easy) |
| 2 | opus / sonnet | math word problems | 1.0 from the baseline (too easy) |
| 3 | opus / sonnet | skill Q&A | 0.727 to 1.0, but the dataset was Opus-generated (see bug below); holdout 0.40/0.60 original vs 0.40/0.60 best |
| 4a | opus / haiku | skill Q&A | 0.845 to 1.0, same dataset bug; holdout original 0.333 vs best 0.200 |
| 4b | opus / haiku | skill Q&A, **fixed grounded dataset** | 0.127, 0.136, 0.264, 0.664, 0.955, 1.000; holdout (3 reps) original 0.20/0.20/0.40 vs best 0.40/0.40/0.40 |

Run 4b conclusion: the loop works mechanically, but the Optimizer pasted **9 of 11 training answers** into the best prompt as a lookup table ("Implementation Reference" plus "never say not documented, give a best guess"). Holdout barely moved (1 of 5 improved: `.observer.pid`). It also deleted most explanatory content ("When to Activate" etc.), so the result is not usable as a skill. The prompt under test cannot learn facts that live only in files the Optimizer never sees; it can only memorize failure samples.

## Bugs and gotchas found (verified)
- `run()` regenerated the dataset every time (fixed by `reuse_dataset`). The Optimizer writes the dataset from `task.description` ONLY.
- `contains` metric (`src/metrics.py:_contains`): 1.0 if the label is inside the answer; else a number fallback (digit from the label found ANYWHERE in the answer scores 1.0: "Not documented in v2.1" scores 1.0 against `exit 2`); else token-overlap partial credit (0.5/0.3/0.1; "is not running" earned 0.5 against "is running"). Use identifier labels: letters, 4+ chars, max 3 words, no digits, no `=`.
- Iteration 1 re-tests the baseline prompt ("Duplicate experiment detected"), so `max_iterations: 5` gives 4 new prompts.
- Significance gate: improvements often log "not yet statistically significant"; `best_prompt` (raw best, drives UI) can differ from `stat_best_prompt`. The scipy `Precision loss` warning appears when one score list is constant; harmless.
- `Config.to_yaml` writes `api_key: null` into every LLM block, so `LocalLLMConfig` configs cannot be loaded back (pre-existing bug, not fixed; `ClaudeCLIConfig` has an `api_key` field for this reason).
- The ledger file was not found at the configured path after one run although the log named it. Cause not investigated.

## Where things are
- Durable: `/data/data/com.termux/files/home/autoprompter-experiments/` has `dataset_run4/` (`train.json` 11 entries, `holdout.json` 5, `config_haiku.yaml`), `scripts/` (`gen_dataset.py` builds the grounded dataset from `raw_opus.txt` with strict label checks; `eval_holdout.py MODEL RUN_DIR` scores original vs best prompt on holdout; `run_fixed_dataset.py` runs a fixed dataset without the repo flag; `make_config.py`), `results/` (final reports, best prompts, logs, `prompt2.diff`), `patches/`. The config in `dataset_run4/config_haiku.yaml` has absolute paths into the deleted job temp folder; fix `storage.*` paths before reuse, and with the new flag add `reuse_dataset: true` and drop the subclass runner.
- Raw copies: `autoprompter-experiments/run1/` to `run4/` hold the unsorted job-temp folders (run1 sentiment, run2 math, run3 first Sonnet run, run4 both Haiku runs, with every log, config and diff). `dataset_run4/`, `scripts/`, `results/` and `patches/` above are the sorted subset; the raw folders are safe to delete once nothing is needed from them.
- Run recipe: from `~/AutoPrompter`, `python3 main.py -c <config.yaml> -v -o experiment.reuse_dataset=true -o storage.ledger_file=<abs path> -o storage.results_dir=<abs path>`, started in the background with the log in a file. A 5-iteration Opus/Haiku run takes about 15 minutes. `claude` is `~/.local/bin/claude` (2.1.289); `opencode` is not installed (the user once mixed its name up with OpenRouter).
- Ephemeral (job temp, gone with the job): `/data/data/com.termux/files/home/.claude/jobs/a5f0acbf/tmp/`.

## Working rules the user set (obey)
- Skill first (the `autoprompter` skill, `simple-english`, `token-diet` were used this session), then explore.
- Always read diffs to the last line (write to a file, `wc -l`, read it all). Run `pwd`/real output before naming a cause; ask for a paste when output is withheld.
- Never push to `origin`; never merge or push without the user. Background-session rules: use a worktree for code edits; git commands from inside an `EnterWorktree` session are blocked for the agent (the user then runs short one-line `!` commands themselves; lines must start with `!`, stay short, and avoid trailing text because zsh treats `(...)` as a glob). From the main checkout, read-only git works.
- Commit trailers: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` (plus `Claude-Session:` line if the reminder gives one). The user writes short commit messages.
- `$CLAUDE_JOB_DIR` became empty mid-session; use explicit paths.

## Suggested next steps (ask the user which)
1. Cleanup worktrees and branches; decide whether to `git push mine main`.
2. Redesign the skill experiment to avoid memorization: put some questions' facts in `task.description` honestly, add a holdout check inside the loop, or optimize for a different goal (a shorter prompt with equal accuracy), and keep `SKILL.md` structure sections out of the Optimizer's reach.
3. Optionally fix `to_yaml` for `LocalLLMConfig` and the stricter metric as upstream-quality patches (on the fork).
