# Research brief: datasets and systems for prompt optimization, compared with AutoPrompter

Refined from the user's prompt on 2026-10-05 and run with deep-research. Output: `notes/Prompt optimization datasets and systems.md`; source notes in `notes/research_notes/`.

Original prompt: "research how other datasets for the purpose of prompt optimization training are build and compare to our way of doing them and what they output. research also how other (recognized, efficacity proven) prompt optimization system (whole codebase) work to compare with the way we do it."

```markdown
# Research brief: datasets and systems for prompt optimization, compared with AutoPrompter

## Context: how AutoPrompter works today
- Loop: an Optimizer LLM rewrites a prompt. A Target LLM answers a dataset with that prompt. A metric
  scores the answers. The Optimizer sees the failures and the experiment history, then rewrites again.
  The main loop calls only `optimize()`. It does not use the candidate-population API.
- Dataset, default: the Optimizer generates input/expected_output pairs from `task.description` alone.
  The set is regenerated on every run, there is no holdout set, and the prompt is optimized on the same
  data it is scored on.
- Dataset, our fix: a "grounded" set. Opus writes questions from source files. A label is kept only
  if it appears word for word in its source, is absent from the prompt, has 4+ characters and at most
  3 words, and has no digits or "=". The set is split 2:1 into train and holdout and loaded with
  `reuse_dataset: true`.
- Metric: `contains`, with a digit fallback and partial credit for word overlap. It is known to be leaky.
- Observed failure: the train score went from 0.13 to 1.0, but holdout went only from about 0.27 to
  0.40. The Optimizer memorized 9 of 11 training answers into the prompt and deleted sections the
  metric did not test.

## Part 1: datasets used to optimize and evaluate prompts
For each method, say how its datasets are built and what it outputs:
- Source: human-labeled benchmarks (BBH, GSM8K, Instruction Induction, HotPotQA, IFEval and similar),
  LLM-synthesized data, or bootstrapped from the program's own traces (DSPy demos).
- Size and splits: train/val/test sizes, whether a holdout is used during optimization, and how
  over-fitting to the train set is detected.
- Label quality: how labels are checked, how much the evaluation relies on exact match, a judge LLM
  or a programmatic metric, and how known metric exploits are prevented.
- Output of the optimization: one instruction, instruction plus few-shot demos, a population or
  Pareto set, or textual "gradients".
Then compare these with both of our dataset methods. Flag where ours is weaker, and where it is
equal or better.

## Part 2: established prompt-optimization systems (whole codebase, not only the paper)
Include only systems that have a peer-reviewed paper or wide adoption plus published benchmark gains.
Candidates: DSPy (MIPROv2, COPRO, BootstrapFewShot), GEPA, TextGrad, OPRO, APE, ProTeGi/APO,
PromptAgent, EvoPrompt, PromptWizard, AdalFlow. Add others that meet the bar.
For each system, report:
1. Loop structure: proposal step, selection, population or single-candidate, how it stops.
2. How it uses feedback: scalar score, error examples, critiques written as text, traces.
3. Steps it takes to avoid over-fitting and memorization: validation split, minibatching, holdout
   selection, regularization of prompt length.
4. Cost: LLM calls per iteration and the typical budget.
5. Reported gains: on which benchmarks and models, and how large compared with the baseline.
6. The code: the main module and file paths, how a metric plugs in, the output artifact.

## Deliverables
- Table A: dataset construction, one row per system plus our two methods.
- Table B: optimizer mechanics, the same rows, with the columns from Part 2.
- Ranked gaps in AutoPrompter. For each gap: the evidence (cite the paper section or the file in the
  repo), the concrete change to make, and the expected effect on holdout score.
- Separate the evidence: peer-reviewed results, results reproduced by third parties, and claims from
  a README only.
- Cite every factual claim with a link. Write "unknown" instead of guessing.

## Out of scope
Fine-tuning or weight-update methods, closed commercial tools with no code, and blog posts with no
benchmark.
```
