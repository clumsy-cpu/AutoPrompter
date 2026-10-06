# Experiments with the claude_cli backend (2026-10)

All runs used `backend: claude_cli`. Files: `~/autoprompter-experiments/` (sorted: `dataset_run4/`, `scripts/`, `results/`, `patches/`; raw job folders: `run1/` to `run4/`).

## Results

| Run | Optimizer / Target | Task | Result |
|---|---|---|---|
| 1 | sonnet / haiku | default sentiment | 1.0 from baseline (too easy) |
| 2 | opus / sonnet | math word problems | 1.0 from baseline (too easy) |
| 3 | opus / sonnet | skill Q&A (Optimizer-written dataset) | 0.727 to 1.0; holdout original 0.40/0.60 vs best 0.40/0.60 |
| 4a | opus / haiku | skill Q&A (Optimizer-written dataset) | 0.845 to 1.0; holdout original 0.333 vs best 0.200 |
| 4b | opus / haiku | skill Q&A, grounded fixed dataset (11 train / 5 holdout) | 0.127, 0.136, 0.264, 0.664, 0.955, 1.000; holdout (3 reps) original 0.20/0.20/0.40 vs best 0.40/0.40/0.40 |

Task in runs 3-4: optimize `~/skills/continuous-learning-v2/SKILL.md` as the prompt so the Target answers implementation questions.

## Lessons

1. **Frontier targets saturate easy tasks.** Sonnet/Haiku score 1.0 on the bundled sentiment and math tasks from the baseline. Use a task where the baseline scores < 0.7.
2. **Optimizer-written datasets are self-graded.** Without `reuse_dataset`, the Optimizer writes questions from `task.description` only, so it tests what it already believes. Build the dataset from ground-truth files and load it with `reuse_dataset: true`.
3. **Training score ≠ generalization.** Run 4b reached 1.0 on train, but 9 of 11 training labels were pasted into the best prompt as an "Implementation Reference" lookup table, plus "never say not documented, give a best guess". Holdout moved 1 of 5 (`.observer.pid`, which leaked by accident). Always keep a holdout set and check label leakage (`eval_holdout.py` does both).
4. **The Optimizer deletes content the metric does not test.** The best prompt dropped "When to Activate" and other explanatory sections, so it was unusable as a skill. Score what you want kept, or keep those sections out of the optimized text.
5. **The prompt cannot learn facts it never sees.** Facts that live only in files the Optimizer and Target cannot read can only be memorized from failures. Put the facts in `task.description` or the prompt honestly, or optimize a different goal (for example, a shorter prompt at equal accuracy).
6. **`contains` digit fallback is real in practice.** In 4b, the original prompt's refusal ("I don't see the specific Python expression...") scored 1.0 against `hexdigest()[:12]` while giving no answer: the label has no exact match, so the score came from the digit fallback (the full reply, truncated in the log, presumably contained `12`). See "Metric Gotchas" in SKILL.md.
7. **Cost/time:** a 5-iteration Opus/Haiku run takes about 15 minutes.

## Scripts (`~/autoprompter-experiments/scripts/`)

| Script | Use |
|---|---|
| `gen_dataset.py` | Builds a grounded Q&A set from Opus output (`raw_opus.txt`). Keeps a label only if it is verbatim in its source file, absent from SKILL.md, letters + 4+ chars + max 3 words, no `=`; splits train/holdout 2:1. |
| `eval_holdout.py MODEL RUN_DIR` | Scores original vs best prompt on holdout (3 reps) and reports which train/holdout labels leaked into the best prompt. |
| `run_fixed_dataset.py` | Ran a fixed dataset before `reuse_dataset` existed. Obsolete: use the flag. |
| `make_config.py` | Writes a run config. |

Hardcoded paths in these scripts point at a deleted job temp folder (`~/.claude/jobs/a5f0acbf/tmp/`); pass `RUN_DIR` or fix `OUT` before reuse. `dataset_run4/config_haiku.yaml` has the same problem in `storage.*`.

## Run recipe

```bash
cd ~/AutoPrompter
python3 main.py -c <config.yaml> -v \
  -o experiment.reuse_dataset=true \
  -o storage.ledger_file=<abs path> -o storage.results_dir=<abs path> \
  > <log> 2>&1 &
```
With `reuse_dataset`, set `batch_size` to the number of entries in `storage.dataset_file`.
