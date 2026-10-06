# Textual feedback / reflection prompt optimizers: GEPA, TextGrad, ProTeGi (APO)

Evidence labels: [peer-reviewed] = ICLR/EMNLP/Nature; [preprint] = arXiv version read; [code] = read from source files on GitHub (via a summarizing fetch tool, so paraphrased not verbatim except where quoted); [docs] = README/doc page. Page numbers are not given; section names are from the PDFs I extracted text from.

## 1. Loop structure (proposal, selection, population, stopping)

### Takeaway
GEPA = population of candidates, reflective LLM mutation on a 3-example train minibatch, minibatch gate, then full eval on a separate Pareto/val set, instance-wise Pareto-frontier sampling of parents. ProTeGi = beam (b=4) of prompts, expand by LLM "gradient" critiques + edits + paraphrases, bandit selection on sampled train data. TextGrad = single prompt, greedy minibatch SGD with a validation check that reverts a bad step.

### Cited Findings
**GEPA** (ICLR 2026 Oral [peer-reviewed]; text read from arXiv PDF)
- Inputs: system, Dtrain, metric mu, a feedback function mu_f, rollout budget B. Hyperparams: minibatch size b, Pareto set size n_pareto. Dtrain is split into D_feedback (signal) and D_pareto (selection). Only prompts evolve; weights frozen. — [GEPA paper Sec. 3, Alg. 1](https://arxiv.org/pdf/2507.19457)
- Per iteration (Alg. 1): SelectCandidate from pool; pick module (round-robin policy); sample minibatch of size b from D_feedback; run candidate with traces and mu_f; reflection LM rewrites the module prompt; compare avg minibatch score before/after; only if improved, add to pool with parent record and evaluate on all of D_pareto. Final answer = candidate with best average score on D_pareto. — [GEPA paper Alg. 1, Fig. 4](https://arxiv.org/pdf/2507.19457)
- Reflection LM is shown (current prompt, program trajectory, score, feedback) and asked to attribute successes/failures to prompt elements and propose revised instructions. — [GEPA paper Sec. 3](https://arxiv.org/pdf/2507.19457)
- Pareto selection (Alg. 2): for each val instance keep the best score over all candidates; keep candidates that are best on at least one instance; prune strictly dominated ones; sample a parent with probability proportional to the number of instances it leads. Paper motivation: always picking the best candidate stalls in a local optimum. — [GEPA paper Sec. 3.1, Alg. 2](https://arxiv.org/pdf/2507.19457)
- Merge ("System Aware Merge", Appendix D.1, Alg. 3/4): crossover of two non-ancestor lineages sharing an ancestor; takes per-module the version that evolved in one lineage but not the other. Max 5 merge invocations in experiments. GEPA+Merge helped GPT-4.1 Mini but hurt Qwen3-8B (e.g. IFBench 38.61 -> 28.23). — [GEPA paper Obs. 5, App. D/E.4, Table 1](https://arxiv.org/pdf/2507.19457)
- Population: yes (candidate tree with ancestry). Experiments used minibatch size 3. Budget stop: rollout budget B; GEPA budget was capped to match MIPROv2's rollout count per benchmark (within 10.15%). — [GEPA paper App. E.4](https://arxiv.org/pdf/2507.19457)
- Code loop (src/gepa/core/engine.py): evaluates seed on valset first; each iteration tries a merge first if `merges_due > 0 and last_iter_found_new_program`, else reflective mutation; default acceptance `StrictImprovementAcceptance` = `new_sum > old_sum` on minibatch scores (alt: `ImprovementOrEqual`); accepted candidates get full valset eval and update the Pareto front; stops when stop callbacks fire (e.g. metric-call budget). — [engine.py](https://raw.githubusercontent.com/gepa-ai/gepa/main/src/gepa/core/engine.py) [code]
- optimize() stop options: must give at least one of `stop_callbacks`, `max_metric_calls`, `max_reflection_cost`. Defaults: `candidate_selection_strategy="pareto"` (also current_best, epsilon_greedy, top_k_pareto), `reflection_minibatch_size` 3, `skip_perfect_score=True`, `module_selector="round_robin"`, `use_merge=False`, `acceptance_criterion="strict_improvement"`, `val_evaluation_policy` -> full_eval. Classes: GEPAEngine, ReflectiveMutationProposer, MergeProposer. — [api.py](https://raw.githubusercontent.com/gepa-ai/gepa/main/src/gepa/api.py) [code]

**ProTeGi / APO** (EMNLP 2023 [peer-reviewed]; text read from arXiv v2)
- Algorithm 1: beam search, beam width b, depth r. Each step: every prompt in beam is expanded (Alg. 2), then Select_b picks next beam. Output = argmax metric in final beam. — [Pryzant et al.](https://arxiv.org/pdf/2305.03495)
- Expand: sample a minibatch D_mini from train; run prompt; collect errors; feed errors to a static feedback prompt "nabla" that describes flaws -> m "gradients" (text); a second prompt "delta" edits the prompt per gradient (q edits); then a paraphrase LLM adds Monte Carlo successors. — [Pryzant et al. Sec. 2.1-2.2.1](https://arxiv.org/pdf/2305.03495)
- Selection treated as best-arm identification: UCB, UCB-E, Successive Rejects, Successive Halving, vs uniform. Arms = candidate prompts, pull = evaluate on random train data points. — [Pryzant et al. Sec. 2.2.2, Alg. 3-4](https://arxiv.org/pdf/2305.03495)
- Defaults in paper: minibatch 64, beam 4, 6 optimization steps, groups of 4 errors per gradient, 4 gradients per error group, 1 edit per gradient, 2 MC samples per candidate, 8 successors sampled per parent before bandit selection, UCB c=2.0 in the paper. Dev 50 / test 150 examples per task, 3 trials, gpt-3.5-turbo, temperature 1.0 for optimizer calls. — [Pryzant et al. Sec. 3.2, Sec. 3.4](https://arxiv.org/pdf/2305.03495)
- Repo defaults (main.py): rounds=6, beam_size=4, minibatch_size=64, n_test_exs=400, max_threads=32, c=1.0 (differs from the paper's c=2.0 for the experiments). — [LMOps main.py](https://raw.githubusercontent.com/microsoft/LMOps/main/prompt_optimization/main.py) [code]
- Stop: fixed number of rounds; no convergence test described. Paper notes all datasets peaked around step 3 and the process "can begin to overfit on the train data, or get caught in a local minima". — [Pryzant et al. Learning Curves](https://arxiv.org/pdf/2305.03495)

**TextGrad** (arXiv v1 June 2024 [preprint]; Nature 2025 vol 639 pp 609-616 [peer-reviewed, citation taken from the repo README, I did not open the Nature page; it redirected to a login])
- Single variable (the prompt) updated by Textual Gradient Descent (TGD): forward pass over a minibatch; per-instance loss (an LLM-evaluated or exact-match loss); `tg.sum` concatenates the per-instance gradients; backward pass produces a text gradient on the prompt; TGD optimizer LLM rewrites it. Options: momentum (earlier iterations visible to optimizer), natural-language constraints. — [TextGrad arXiv Sec. 2 "Optimization Techniques"](https://arxiv.org/pdf/2406.07496)
- Prompt-optimization setup: batch size 3, 12 iterations (36 training examples sampled with replacement); after each iteration run the validation set and update the prompt only if validation performance is better than the previous iteration. Forward model gpt-3.5-turbo-0125, gradient/optimizer model gpt-4o. — [TextGrad arXiv Sec. 3.3](https://arxiv.org/pdf/2406.07496)
- Code: `TextualGradientDescent(parameters, engine, constraints, gradient_memory=0, ...)`; `step()` builds an update prompt from variable description/value/gradient/constraints, calls the engine, extracts text between `<IMPROVED_VARIABLE>` tags, sets the value; a separate `TextualGradientDescentwithMomentum` keeps a window of past values. — [optimizer.py](https://raw.githubusercontent.com/zou-group/textgrad/main/textgrad/optimizer/optimizer.py) [code]
- GEPA paper characterizes TextGrad as "SelectBestCandidate" (evolve only the top candidate) and APO as BeamSearch(N=4). — [GEPA paper Obs. 3](https://arxiv.org/pdf/2507.19457)

### Inferences
- AutoPrompter is structurally closest to TextGrad/greedy "SelectBestCandidate" (one candidate), but lacks TextGrad's accept-only-if-validation-improves revert and GEPA's minibatch gate. GEPA's own ablation (below) shows single-candidate greedy gets about half the gain of Pareto selection.
- AutoPrompter's "diverse strategy after 5 stagnant iterations" is a weak substitute for GEPA's per-instance Pareto sampling or ProTeGi's beam.

### Gaps
- Exact text of GEPA's reflection meta-prompt (Appendix C figure) not extracted; the repo template is only paraphrased: "I provided an assistant with the following instructions to perform a task for me ... Provide the new instructions within ``` blocks." ([instruction_proposal.py](https://raw.githubusercontent.com/gepa-ai/gepa/main/src/gepa/strategies/instruction_proposal.py))
- ProTeGi repo optimizers.py: the fetch summary reported no bandit implementation, yet main.py has bandit-style args (eval_rounds, samples_per_eval, c). Unresolved which selection algorithms the released code actually implements.

## 2. Feedback: scalar vs textual

### Takeaway
GEPA extends the metric to a feedback function mu_f returning score plus text (compiler errors, failed rubrics, per-constraint results). ProTeGi's "gradient" is an LLM critique generated from the raw error examples only (no metric text). TextGrad's loss is itself an LLM critique or an eval whose result is back-propagated as text.

### Cited Findings
- GEPA: mu_f "extracts textual traces during evaluation and returns them with the final score as feedback_text"; can be module-specific (e.g. per hop in multi-hop); human explanations can be added to Dtrain as feedback_text. Example: IFBench feedback lists which constraints were satisfied and which failed. — [GEPA paper Sec. 3, App. E.1](https://arxiv.org/pdf/2507.19457)
- GEPA code: adapter `evaluate(batch, candidate, capture_traces)` returns `EvaluationBatch(outputs, scores, trajectories, objective_scores, num_metric_calls)`; `make_reflective_dataset(candidate, eval_batch, components_to_update)` returns a per-component JSON-serializable list of examples shown to the reflection LM as markdown ("# Example 1", "## field"). Scores: higher is better; sum for minibatch decisions, mean for validation. — [adapter.py](https://raw.githubusercontent.com/gepa-ai/gepa/main/src/gepa/core/adapter.py), [instruction_proposal.py](https://raw.githubusercontent.com/gepa-ai/gepa/main/src/gepa/strategies/instruction_proposal.py) [code]
- dspy.GEPA metric protocol: `(gold, pred, trace, pred_name, pred_trace)` returning float or `ScoreWithFeedback`; if no feedback is returned the default text is "This trajectory got a score of {score}." — [dspy gepa.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/gepa/gepa.py) [code]
- ProTeGi: gradient prompt takes current prompt plus the error examples (inputs, labels, predictions) and asks for reasons the prompt was wrong ("give {num_feedbacks} reasons why the prompt could have gotten these examples wrong" in the repo); only mismatched examples are used, metric is F1. — [paper Sec. 2.2.1](https://arxiv.org/pdf/2305.03495), [optimizers.py](https://raw.githubusercontent.com/microsoft/LMOps/main/prompt_optimization/optimizers.py) [code]
- TextGrad: loss is natural-language (TextLoss) or exact match / LLM-judge (used for Word Sorting); gradients propagate through the graph as text; for prompt optimization the per-example gradients are summed. — [TextGrad arXiv Sec. 2-3.3](https://arxiv.org/pdf/2406.07496), [README](https://raw.githubusercontent.com/zou-group/textgrad/main/README.md) [docs]

### Inferences
- AutoPrompter's "failure feedback" is closest to ProTeGi's error-example critique. GEPA's distinguishing input is metric-side text explaining why an instance scored low, and traces of intermediate steps.
- Neither paper contains a mechanism that stops the optimizer copying answers into the prompt; the protection in GEPA comes from the separate D_pareto set and the minibatch gate (section 3), not from the feedback format.

### Gaps
- No source found on whether feedback_fn text should avoid leaking gold labels. I found no discussion of this in the GEPA paper text I extracted.

## 3. Anti-overfitting and acceptance

### Takeaway
GEPA separates D_feedback (reflection signal) from D_pareto (selection) and double-gates acceptance (minibatch must improve, then full D_pareto eval decides standing). TextGrad uses a validation check per step. ProTeGi has only train data for selection and test for reporting (no validation split) and admits overfitting after ~3 steps. dspy.GEPA warns that valset=None reuses trainset and overfits.

### Cited Findings
- GEPA: "direct access to the content of validation instances is restricted"; optimizers may only monitor validation scores for selection/early stopping. Splits: train used as D_feedback, val as D_pareto, test held out. IFBench: 150 train / 300 val / 294 test (IF-RLVR train split; IFBench itself as test so unseen constraints are not accessed); PUPA: 111 train examples (rest not extracted). — [GEPA paper Sec. 4, App. E.1](https://arxiv.org/pdf/2507.19457)
- GEPA reports a generalization gap (val minus test) study following Wan et al. 2024 and states reflectively evolved instructions "demonstrate a lower generalization gap" than MIPROv2 (Fig. 16; I did not extract the plotted numbers). — [GEPA paper Obs. 2](https://arxiv.org/pdf/2507.19457)
- GEPA cross-model transfer: prompts optimized on Qwen3-8B and evaluated on GPT-4.1 Mini gave +9.00 aggregate points, above MIPROv2 +5.64, TextGrad +6.11, Trace +3.27 optimized directly on GPT-4.1 Mini. — [GEPA paper Table 2, Obs. 6](https://arxiv.org/pdf/2507.19457)
- GEPA paper itself notes GEPA can deliberately "overfit" when Dtrain=Dpareto=the task set, as an inference-time search mode (e.g. kernel generation). — [GEPA paper Sec. 5.1](https://arxiv.org/pdf/2507.19457)
- dspy.GEPA: "If valset is None, the system uses trainset for both training and validation ... A warning notes this causes overfitting". — [dspy gepa.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/gepa/gepa.py) [code]
- GEPA pruning: prompts from the best optimizers tend to be shorter (up to 9.2x shorter than MIPROv2's few-shot prompts); the paper does not describe measures against deleting prompt sections the metric does not test. — [GEPA paper Obs. 4](https://arxiv.org/pdf/2507.19457)
- TextGrad: per-iteration validation check, update only if better than the previous iteration; splits 50/100/100 train/val/test for BBH tasks; GSM8k 200/300/1319. — [TextGrad arXiv Sec. 3.3, App. E](https://arxiv.org/pdf/2406.07496)
- ProTeGi: no validation split in code (train/test only; test F1 logged each round); paper: 50 dev / 150 test, results are max over the final beam on test; "can begin to overfit ... all datasets peaked at around 3 steps". — [LMOps main.py](https://raw.githubusercontent.com/microsoft/LMOps/main/prompt_optimization/main.py) [code], [paper Sec. 3.2, 3.4](https://arxiv.org/pdf/2305.03495)

### Inferences
- The overfit/memorization failure described for AutoPrompter (train 1.0, holdout flat) is the situation GEPA's design addresses only partially: mutation sees only a 3-example minibatch (so the optimizer cannot see the whole dataset to memorize), and selection uses a separate val set. Neither GEPA nor TextGrad papers show an explicit defence against answer leakage into prompts (not found).
- ProTeGi's reported test numbers pick the max over the final beam on test, which is optimistic selection on the reporting set.

### Gaps
- GEPA Fig. 16 generalization-gap numbers not extracted. No source found for GEPA behavior when val is small/noisy beyond the paper's note that reducing val set size is future work.

## 4. Cost

### Takeaway
GEPA's rollout use is dominated by validation evaluation; the paper claims up to 35x fewer rollouts than GRPO (24,000 rollouts) and rollout parity with MIPROv2 by construction. ProTeGi cost is controlled by bandit selection.

### Cited Findings
- GEPA rollouts (Table 1, Qwen3 8B): GEPA/GEPA+Merge 6871 (HotpotQA), 3593 (IFBench), 7051 (HoVer), 2426 (PUPA), 1839 (AIME-2025), 1839 (LiveBench-Math), aggregate-avg 3936; GRPO 24,000 for all. — [GEPA Table 1](https://arxiv.org/pdf/2507.19457)
- "The majority of GEPA's rollout budget is spent on validation"; train-only rollouts to reach optimum: 79 to 737. GEPA matches GRPO's best validation after 243, 402, 330, 1143, 1179, 306 rollouts (up to 78x). IFBench: 678 rollouts to 38.61% vs GRPO 35.88% at 24,000. — [GEPA Obs. 1, Table 1 caption](https://arxiv.org/pdf/2507.19457)
- Dollar cost (GPT-4.1 mini, Table 2 experiments): total under $500; GEPA $86, GEPA-Merge $67, MIPROv2 $76, Trace and TextGrad $172 combined. — [GEPA App. E.3](https://arxiv.org/pdf/2507.19457)
- GEPA matched compute to MIPROv2 per benchmark by capping rollouts to MIPROv2's count. — [GEPA App. E.4](https://arxiv.org/pdf/2507.19457)
- ProTeGi: efficiency framed as API queries per prompt candidate (12 to 50 evals per candidate in Fig. 3); claims better results with fewer API calls than baselines. Per-step call count is a function of settings above (m gradients x q edits x p MC samples, capped at 8 successors per parent). — [Pryzant et al. Sec. 3.4](https://arxiv.org/pdf/2305.03495)
- TextGrad prompt optimization: 12 iterations x batch 3 = 36 training examples, plus a full validation pass per iteration. — [TextGrad arXiv Sec. 3.3](https://arxiv.org/pdf/2406.07496)
- dspy.GEPA `auto` presets: light = 6 candidates, medium = 12, heavy = 18 (budget computed as metric calls). — [dspy gepa.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/gepa/gepa.py) [code]

### Inferences
- A full-dataset eval per iteration (AutoPrompter) is the costly pattern GEPA avoids on the learning side: it reflects on 3 examples and spends full evals only on gated candidates.

### Gaps
- Per-run LLM call counts for TextGrad and ProTeGi are not reported in a comparable unit; GEPA's TextGrad cost ($172 for Trace+TextGrad combined) is not split.

## 5. Reported gains (benchmarks, models, magnitude)

### Takeaway
GEPA: aggregate +9.62 (Qwen3 8B) and +12.19/+13.33 (GPT-4.1 Mini) points over baseline, beating MIPROv2, TextGrad, Trace, GRPO. All GEPA-vs-baseline numbers are authors' own preprint/ICLR numbers, not independent replication (none found).

### Cited Findings
GEPA Table 1, Qwen3 8B (scores in %) — [source](https://arxiv.org/pdf/2507.19457)
| Method | HotpotQA | IFBench | HoVer | PUPA | AIME-25 | LiveBench-Math | Agg. gain |
|---|---|---|---|---|---|---|---|
| Baseline | 42.33 | 36.90 | 35.33 | 80.82 | 27.33 | 48.70 | - |
| GRPO | 43.33 | 35.88 | 38.67 | 86.66 | 38.00 | 51.26 | +3.68 |
| MIPROv2 | 55.33 | 36.22 | 47.33 | 81.55 | 20.00 | 46.60 | +2.61 |
| GEPA | 62.33 | 38.61 | 52.33 | 91.85 | 32.00 | 51.95 | +9.62 |
| GEPA+Merge | 64.33 | 28.23 | 51.67 | 86.26 | 32.00 | 51.95 | +7.17 |

GEPA Table 2, GPT-4.1 Mini — [source](https://arxiv.org/pdf/2507.19457)
| Method | HotpotQA | IFBench | HoVer | PUPA | AIME-25 | LiveBench-Math | Agg. gain |
|---|---|---|---|---|---|---|---|
| Baseline | 38.00 | 47.79 | 46.33 | 78.57 | 49.33 | 58.20 | - |
| Trace (OptoPrime) | 60.33 | 51.19 | 46.00 | 74.18 | 45.33 | 60.74 | +3.27 |
| MIPROv2-No-Demos | 38.00 | 52.04 | 51.33 | 91.85 | 48.67 | 60.97 | +4.11 |
| MIPROv2 | 58.00 | 49.15 | 48.33 | 83.37 | 51.33 | 61.84 | +5.64 |
| TextGrad | 62.33 | 48.64 | 47.67 | 85.68 | 46.67 | 63.84 | +6.11 |
| GEPA | 69.00 | 52.72 | 51.67 | 94.47 | 59.33 | 64.13 | +12.19 |
| GEPA+Merge | 65.67 | 55.95 | 56.67 | 96.46 | 59.33 | 64.13 | +13.33 |

- Note the aggregate for MIPROv2 on Qwen3 is +2.61, i.e. below GRPO's +3.68, and on AIME-2025 GRPO (38.00) beats GEPA (32.00); the paper's text says GEPA beats GRPO "on all benchmarks except AIME". MIPROv2 drops below baseline on AIME (20.00 vs 27.33). — [GEPA Table 1](https://arxiv.org/pdf/2507.19457)
- Candidate-selection ablation (Qwen3 8B, 4 tasks): SelectBestCandidate +6.05, BeamSearch(N=4) +5.11, GEPA Pareto +12.44 aggregate. IFBench: SelectBest 30.44 (below baseline 36.90). — [GEPA Table 3](https://arxiv.org/pdf/2507.19457)
- Abstract claims: beats GRPO by ~6% average and up to 20%, up to 35x fewer rollouts, beats MIPROv2 by over 10%. — [arXiv abs](https://arxiv.org/abs/2507.19457) (abstract summary via fetch; ICLR 2026 oral)
- ProTeGi: up to 31% improvement over initial prompt; on average beats MC by 3.9% and RL (GrIPS/TEMPERA-style) by 8.2%, initial prompt by 15.3%, AutoGPT by 15.2% (F1, gpt-3.5-turbo, 4 tasks: Jailbreak, Ethos, Liar, Sarcasm). Beam ablation F1: Jailbreak 0.80 (no iteration) / 0.82 (greedy) / 0.85 (beam); Liar 0.63/0.63/0.67; Sarcasm 0.87/0.85/0.88. Bandit table 25 evals/prompt: Unif 0.77/0.59, UCB 0.83/0.66 (Jailbreak/Liar). Base models: Jailbreak F1 GPT-3 0.55, ChatGPT 0.85, GPT-4 0.88. Paper calls itself "limited and preliminary". — [Pryzant et al. Sec. 3.4, Tables 1-3](https://arxiv.org/pdf/2305.03495)
- TextGrad prompt optimization (gpt-3.5-turbo-0125, gpt-4o as gradient engine), accuracy %: Object Counting CoT 77.8, DSPy BFSR 84.9, TextGrad 91.9; Word Sorting 76.7 / 79.8 / 79.8; GSM8k 72.9 / 81.1 / 81.1. — [TextGrad arXiv Table 3](https://arxiv.org/pdf/2406.07496) (preprint v1; the Nature version might report different numbers: not checked)
- TextGrad GSM8k example: optimized prompt after 12 iterations grew from "Think step by step ..." to a multi-sentence procedure (restate, break into steps, verify, notation). — [TextGrad arXiv Sec. 3.3](https://arxiv.org/pdf/2406.07496)

### Inferences
- GEPA's own tables show the "greedy single best candidate" strategy can fall below baseline (IFBench 30.44 vs 36.90), a documented failure of the strategy AutoPrompter resembles.

### Gaps
- No independent replication of GEPA vs MIPROv2/GRPO found in this pass. No ProTeGi or TextGrad results on the GEPA benchmarks other than the GEPA paper's TextGrad column (GPT-4.1 Mini only; no Qwen3 TextGrad row).
- Nature-version TextGrad numbers not verified.

## 6. Code: modules, metric plug-in, output artifact

### Takeaway
GEPA: `gepa.optimize()` in src/gepa/api.py drives GEPAEngine; metric plugs in through a GEPAAdapter (`evaluate` + `make_reflective_dataset`) or via dspy.GEPA's feedback metric. ProTeGi: LMOps/prompt_optimization (main.py, optimizers.py, scorers.py, predictors.py, evaluators.py, tasks.py). TextGrad: pip `textgrad`; Variable, TextLoss, TGD.

### Cited Findings
- GEPA repo layout: `src/gepa/`, `src/gepa/adapters/` (default adapter, DSPy, DSPy full-program, generic RAG, LangChain...), `core/adapter.py` (interface), docs for core (GEPAAdapter, GEPAResult, GEPAState), strategies (selectors, samplers, policies), proposers (LanguageModel, MergeProposer, ReflectiveMutationProposer), callbacks, logging; `.claude/skills/gepa-optimize-anything/`. — [repo](https://github.com/gepa-ai/gepa) [README/tree], [API tree listing](https://api.github.com/repos/gepa-ai/gepa/git/trees/main?recursive=1) (the src tree itself was not seen via the tool; files above were fetched by raw URL)
- GEPA minimal call: `gepa.optimize(seed_candidate, trainset, valset, task_lm / adapter, reflection_lm, max_metric_calls)`; seed_candidate is `dict[str,str]` of named text components (so a single prompt = one key). `valset` may be None (defaults per api.py signature; behavior when None not read). — [api.py](https://raw.githubusercontent.com/gepa-ai/gepa/main/src/gepa/api.py), [README](https://github.com/gepa-ai/gepa) [code/docs]
- Output: `GEPAResult` with candidate(s), per-instance and aggregate val scores, Pareto info, lineage, best outputs per val instance if `track_best_outputs=True`; `run_dir` persists state; optional wandb/mlflow. — [api.py](https://raw.githubusercontent.com/gepa-ai/gepa/main/src/gepa/api.py) [code]
- dspy.GEPA: `dspy.GEPA(metric, reflection_lm, auto|max_full_evals|max_metric_calls, reflection_minibatch_size=3, candidate_selection_strategy="pareto", use_merge=True, max_merge_invocations=5, failure_score=0.0, perfect_score=1.0, track_stats=False, seed=0)`; `compile(student, trainset, valset)` returns an optimized program, with `detailed_results` (candidate lineage, scores, best outputs per val instance) when `track_stats=True`. Note dspy default `use_merge=True` while gepa.optimize default is False. — [dspy gepa.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/gepa/gepa.py) [code]
- ProTeGi repo files: main.py, optimizers.py, scorers.py, predictors.py, evaluators.py, tasks.py, config.py, utils.py; CLI `python main.py --task --data_dir --prompts --out`; flags `--rounds --beam_size --n_test_exs --minibatch_size --gradients_per_error --steps_per_gradient --mc_samples_per_step`; binary classification tasks only; output JSON of per-round candidates, estimated scores, and test F1. — [LMOps/prompt_optimization](https://github.com/microsoft/LMOps/tree/main/prompt_optimization), [main.py](https://raw.githubusercontent.com/microsoft/LMOps/main/prompt_optimization/main.py) [code]
- TextGrad API: `tg.Variable(value, requires_grad, role_description)`, `tg.TextLoss(...)`, `tg.TGD(parameters=[...])`, `loss.backward()`, `optimizer.step()`; install `pip install textgrad`; prompt-optimization loop snippet in paper Code Snippet 2 (batch, per-example loss, `tg.sum`, backward, step, validation check). Metric plugs in as the loss function. — [README](https://raw.githubusercontent.com/zou-group/textgrad/main/README.md), [paper Code Snippet 2](https://arxiv.org/pdf/2406.07496)

### Inferences
- Porting GEPA's ideas to AutoPrompter without adopting the library: (1) split data into feedback minibatch (about 3) and held-out selection set; (2) accept a candidate only if the minibatch sum strictly improves, then eval on the selection set; (3) keep multiple candidates and sample parents by per-instance wins. This is a design inference, not a source claim.

### Gaps
- Did not read GEPAState / Pareto front code, merge proposer code, or the verbatim default reflection prompt. TextGrad repo's prompt-optimization tutorial notebook not read beyond README. The skill "gepars" (Rust port) exists locally but was not used.
