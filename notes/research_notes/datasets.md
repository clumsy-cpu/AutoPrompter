# Dataset construction in prompt-optimization methods vs AutoPrompter

Source quality key: [P] = paper text (arXiv; GEPA is ICLR 2026 oral per its PDF header; others arXiv preprints/published, venue not verified here); [C] = official source code read at main branch; [D] = docs/README (vendor claim); [3P] = third-party/low trust. WebFetch summaries of docs pages were cross-checked against source text where noted.

## 1. Which benchmarks does each method use, and where do labels come from?

### Takeaway
Every established method optimizes on pre-existing human-labelled benchmarks (BBH, GSM8K, Instruction Induction, HotpotQA, HoVer, classification sets). Only the DSPy bootstrap family derives extra "labels" (intermediate-step demos) from program traces, and only PromptWizard synthesizes new few-shot examples with an LLM. None of the surveyed papers builds a whole eval set from a task description alone, which is what AutoPrompter's default does.

### Cited Findings
- APE: Instruction Induction tasks plus a 21-task BIG-Bench subset; baselines use human "gold annotations" [P] — [APE](https://arxiv.org/abs/2211.01910)
- OPRO: GSM8K and BBH (human labels); linear regression uses 50 synthetic data points generated programmatically [P] — [OPRO](https://arxiv.org/abs/2309.03409)
- ProTeGi: Jailbreak (452 examples, human-annotated labels), Ethos (997), Liar (4000), Sarcasm (10,000) — all existing labelled datasets [P] — [ProTeGi](https://arxiv.org/pdf/2305.03495)
- PromptAgent: BBH tasks plus domain tasks (NCBI, Biosses, MedQA) and general NLP (Subj, TREC, CB); existing labelled sets [P] — [PromptAgent](https://arxiv.org/pdf/2310.16427)
- EvoPrompt: language-understanding and generation datasets (SST-5, Subj, ASSET, etc.) and 23 BBH tasks [P] — [EvoPrompt](https://arxiv.org/pdf/2309.08532)
- TextGrad prompt optimization: Object Counting and Word Sorting (BBH) and GSM8K; GSM8K splits come from DSPy [P] — [TextGrad](https://arxiv.org/pdf/2406.07496)
- MIPROv2 paper: HotPotQA (fullwiki), HotPotQA Conditional (hand-labelled, so smaller), Iris, Heart Disease, ScoNe, HoVer (three-hop filtered) [P] — [MIPRO](https://arxiv.org/pdf/2406.11695)
- MIPRO/DSPy demos are bootstrapped by rejection sampling: inputs run through the program, and if the output scores high enough on the metric, all values in the trace become candidate labelled demonstrations. This avoids needing gold labels for intermediate stages [P] — [MIPRO](https://arxiv.org/pdf/2406.11695)
- GEPA: AIME-2025, LiveBench-Math, HotpotQA, IFBench, HoVer, PUPA (PAPILLON) with existing compound systems and hand-written feedback functions; most benchmarks "obtained from Tan et al. (2025)" [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- GEPA IFBench: train/val come from IF-RLVR Train, IFBench is the test set "to ensure that the optimizers do not access the new, unseen constraints being tested" [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- GEPA can optionally consume human-written explanations per training instance as auxiliary feedback text [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- PromptWizard: BBII (19 tasks), 23 BBH tasks, GSM8K, AQUARAT, SVAMP, plus Ethos, PubMedQA, MedQA, CSQA, SQA, 6 MMLU medical subsets; human labels. Optimizes with 25 randomly chosen training examples [P] — [PromptWizard](https://arxiv.org/pdf/2405.18369)
- AdalFlow docs: BBH Object Count (50/50/100), HotPotQA, TREC [D] — [AdalFlow docs](https://adalflow.sylph.ai/use_cases/question_answering.html)

### Inferences
- Labels in the literature are independent of the optimizer LLM (human, or programmatic verifiers). AutoPrompter's default has the optimizer LLM author both questions and answers, a circularity absent from every method above.
- AutoPrompter's "grounded" set (Opus writes Q&A from source files, verbatim-in-source check) is closer to a proper external-label setup, but its labels are still LLM-written, and the filter keeps only extractive short-span answers (a narrow task distribution).

### Gaps
- Exact BBH split sizes in EvoPrompt and APE beyond what is quoted below were not extracted.

## 2. Exact train/val/test sizes and use of a held-out set during optimization

### Takeaway
Nearly all methods keep a separate test set that is never seen during optimization. Most also keep a distinct selection set (dev/val). Using the same data to optimize and to report (AutoPrompter default) is not done by any of the surveyed methods, with one exception where it is explicitly flagged as overfitting (DSPy GEPA with valset=None). Note one counter-example: EvoPrompt's BBH dev set is sampled from the test set.

### Cited Findings
- GEPA: HotpotQA 150 train / 300 val / 300 test; IFBench 150 / 300 / 294; HoVer 150 / 300 / 300; PUPA 111 / 111 / 221; AIME: 2022-24 questions (90) split equally train/val, AIME-2025 (30 questions, each repeated 5 times) as test; LiveBench-Math 368 questions split equally train/val/test [P] — [GEPA appendix E.1](https://arxiv.org/pdf/2507.19457)
- GEPA uses the validation set for candidate selection: "optimizers may monitor the performance of candidate parameters ... by tracking scores on the validation set", but "direct access to the content of validation instances is restricted"; Algorithm 1 splits Dtrain into Dfeedback and Dpareto (|Dpareto| = n_pareto), and the Pareto front is kept per-instance over Dpareto; the final candidate maximizes mean Dpareto score [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- GEPA: reflection uses a minibatch from the train split; the majority of the rollout budget is spent on validation scoring used only for selection; the paper reports a validation-vs-test generalization gap analysis [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- DSPy GEPA (code): if valset is None it warns it is "Using trainset as valset", which "makes GEPA overfit prompts to the provided trainset" and says to "provide separate trainset and valset"; recommends the smallest valset that matches the downstream distribution and as large a trainset as possible; reflection_minibatch_size default 3 [C, via WebFetch summary of source] — [gepa.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/gepa/gepa.py)
- MIPROv2 paper: HotPotQA 500 train / 500 dev / 2000 test; HotPotQA Conditional 500 / 200 / 200; Iris 75 / none / 75; Heart Disease 120 / none / 183; ScoNe 500 / 500 / 1200; HoVer 500 / 500 / 1520. "Dev data was used as a development set to internally iterate on methods"; test only for final evaluation [P] — [MIPRO Table 3](https://arxiv.org/pdf/2406.11695)
- MIPROv2 paper: candidates are scored on the training set "or a dedicated validation split thereof"; stochastic minibatch scoring with periodic full evaluation; 50 full-eval trials for HotPotQA/ScoNe, 30 for Iris/Heart/HotPotQA-Cond, 20 for HoVer (this is per the paper's budget statement, ~300 minibatch trials for 50 full) [P] — [MIPRO](https://arxiv.org/pdf/2406.11695)
- DSPy MIPROv2 code: if valset is None, `valset_size = min(1000, max(1, int(len(trainset)*0.80)))`, `valset = trainset[cutoff:]`, `trainset = trainset[:cutoff]`. I read this in the raw source: the default is 80% validation / 20% train (the opposite of the usual convention), and the train part feeds proposal and bootstrapping while the val part scores candidates. Defaults: minibatch_size=35, minibatch_full_eval_steps=5, max_bootstrapped_demos=4, max_labeled_demos=4; auto presets light/medium/heavy cap val size at 100/300/1000; minibatching raises an error if minibatch_size > len(valset) [C] — [mipro_optimizer_v2.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/mipro_optimizer_v2.py) (the WebFetch summary first misreported this as 80% train; the raw file check corrects it)
- DSPy COPRO (code): candidates are evaluated on the supplied trainset directly, no separate valset; defaults breadth=10, depth=3, init_temperature=1.4 [C, via WebFetch summary] — [copro_optimizer.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/copro_optimizer.py)
- DSPy BootstrapFewShot (code): defaults max_bootstrapped_demos=4, max_labeled_demos=16, max_rounds=1, optional metric_threshold; examples that fail to bootstrap fall back as raw labelled demos [C, via WebFetch summary] — [bootstrap.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/bootstrap.py)
- TextGrad: Object Counting/Word Sorting randomly split 50/100/100 train/val/test; GSM8K uses DSPy splits 200/300/1319; batch size 3 for 12 iterations (36 training examples seen); after each iteration a validation loop runs, and the prompt is updated only if validation performance improves [P] — [TextGrad](https://arxiv.org/pdf/2406.07496)
- OPRO: GSM8K uses 3.5% of the 7,473-example train set for optimization, test = 1,319; BBH uses 20% of examples for optimization, the rest for testing; training accuracy is typically 5-20% above test accuracy [P, via WebFetch summary] — [OPRO](https://arxiv.org/html/2309.03409)
- APE: instruction proposals from 5 input-output pairs; evaluated with "50 train, 50 eval" in the proposal-quality analysis; execution accuracy aligned better with test performance than log-prob; reports held-out test results [P, via WebFetch summary; exact per-task split not verified] — [APE](https://arxiv.org/html/2211.01910)
- ProTeGi: per task, 50 random examples for development and 150 for test; results averaged over 3 trials; test binary F1; minibatch 64, beam 4, 6 steps, groups of 4 errors, 4 gradients per group; few-shot examples (a random pair) held constant [P] — [ProTeGi](https://arxiv.org/pdf/2305.03495)
- PromptAgent: reward is "task performance on a held-out set separated from the given training samples"; held-out reward subset default 150 (range 60-200); test sets are official splits (capped at 1000) or about half the data. Example splits (train/test): Penguins 70/79, Geometry 150/200, Epistemic 500/500, Object counting 300/500, Temporal 300/500, Causal judgement 90/100, NCBI 2000/940, Biosses 60/40, MedQA 2000/500, Subj 400/1000, TREC 400/500, CB 125/56 [P] — [PromptAgent Appendix A.2](https://arxiv.org/pdf/2310.16427)
- EvoPrompt: fitness uses a development set (size 200 for the classification/generation tasks); best dev prompt is reported on the test set; for BBH "we sample a subset from the test set as the development set", i.e. dev overlaps test there [P] — [EvoPrompt](https://arxiv.org/pdf/2309.08532)
- PromptWizard: only 25 training examples used to optimize ("We do not use entire training dataset"), mini-batches of 5 for scoring, evaluation on the full test set; baselines keep their own splits [P] — [PromptWizard](https://arxiv.org/pdf/2405.18369)
- AdalFlow: validator checks proposals on the val set before accepting; a "constrained" strategy subsamples val to at most 4 correct and 4 failed examples for a cheap pre-check [D] — [AdalFlow docs](https://adalflow.sylph.ai/use_cases/question_answering.html)

### Inferences
- AutoPrompter's 2:1 train/holdout is split reasonably, but the sizes (about 11 train labels, per the observed 9/11) are far below GEPA's 111-150 train and 111-300 val, and below MIPRO's 500/500. A holdout of a handful of items gives very noisy estimates; the observed 0.27 -> 0.40 holdout gain may be within noise (cannot be computed without actual holdout size, which was not given).
- The three-way split (train for feedback, val for selection, test never touched) is standard. AutoPrompter uses only two sets, so if the holdout also drives selection it becomes a validation set and loses test status.
- Memorization of 9/11 labels is the failure mode the literature guards against by (a) restricting the optimizer's view of validation content (GEPA) and (b) holding out a test set; OPRO and PromptAgent still observe train-test gaps.

### Gaps
- GEPA minibatch size and n_pareto defaults in the paper text were not extracted (the DSPy default of 3 for reflection minibatch is from code).
- APE per-task exact train/test sizes not verified.

## 3. Handling few labelled examples

### Takeaway
DSPy documents tiers by data volume (about 10 examples, 50+, 200+); PromptWizard explicitly supports 0-example, synthetic-example, and with-data modes and reports degradation from 25 to 5 examples as modest. DSPy has no first-party synthetic-data guarantee in what I could verify.

### Cited Findings
- DSPy optimizer guide: with "~10" examples start with BootstrapFewShot; with 50+ try BootstrapFewShotWithRandomSearch; MIPROv2 for instruction-only optimization (0-shot configuration); for longer runs (40+ trials) use MIPROv2 with "enough data (e.g. 200 examples or more to prevent overfitting)" [D, via WebFetch of raw docs] — [optimizers.md](https://raw.githubusercontent.com/stanfordnlp/dspy/main/docs/docs/learn/optimization/optimizers.md)
- DSPy data docs: state only that you need "at least a few example inputs" and mention train/dev/test sets, with no quantitative split ratios [D, via WebFetch] — [data.md](https://raw.githubusercontent.com/stanfordnlp/dspy/main/docs/docs/learn/evaluation/data.md)
- PromptWizard: three scenarios (no examples, synthetic examples, with training data); `seen_set_size` suggested 25; training data as .jsonl with question/answer; users implement answer extraction/comparison classes [D] — [PromptWizard README](https://github.com/microsoft/PromptWizard)
- PromptWizard paper: synthetic few-shot examples generated by a critique-and-synthesize loop (positive/negative examples from performance, critique, new synthetic examples), initial pool of 25 random examples; with only 5 training examples per dataset it shows "only" a modest drop versus 25 [P] — [PromptWizard](https://arxiv.org/pdf/2405.18369)
- PromptWizard's own task-description-only mode exists in the README ("optimizing prompts without examples") but the paper's benchmark results all use labelled training data; no peer-reviewed evaluation of the no-data mode was found [D vs P] — [README](https://github.com/microsoft/PromptWizard)
- APE builds instruction candidates from only 5 input-output demonstrations [P, via summary] — [APE](https://arxiv.org/html/2211.01910)
- MIPRO 0-shot mode still needs a training set to ground proposals (dataset-descriptor prompt loops over training batches) [P] — [MIPRO](https://arxiv.org/pdf/2406.11695)
- A third-party DSPy skills page says to use synthetic data when you have fewer than 200 labelled examples and warns that synthetic data inherits the generator LM's biases [3P, low trust] — [skillselion](https://skillselion.com/skills/lebsral/dspy-programming-not-prompting-lms-skills/ai-generating-data)

### Inferences
- The literature never treats LLM-synthesized evaluation labels as ground truth for reporting; PromptWizard's synthetic items are used as few-shot demos inside the prompt, not as an eval set. AutoPrompter's default (synthetic eval set, scored on itself) has no analogue.
- Given 10-25 labelled examples is the common regime (DSPy ~10, PromptWizard 25, GEPA 111-150), AutoPrompter's ~11 train items match the lower end, but others pair that with a clean external test.

### Gaps
- I did not find an official DSPy synthetic-data generator doc (dspy.ai pages returned navigation stubs through WebFetch).

## 4. Metric definitions and guards against gaming

### Takeaway
Metrics are exact match / accuracy / F1, programmatic verifiers, or LLM judges; explicit anti-gaming defenses are mostly structural (held-out sets, OOD test constraints, hidden validation content), not metric-level. Nobody in this set uses a lenient substring/token-overlap metric as the main score.

### Cited Findings
- MIPRO paper: Exact Match for HotPotQA, HotPotQA Conditional and ScoNe; accuracy for Iris/Heart Disease; Retrieval@21 (gold-document recall) for HoVer [P, via summary] — [MIPRO](https://arxiv.org/html/2406.11695)
- TextGrad: string-based exact match for GSM8K and Object Counting (final number equals ground truth); an LLM compares response to ground truth for Word Sorting [P] — [TextGrad](https://arxiv.org/pdf/2406.07496)
- ProTeGi: binary F1 on the test set [P] — [ProTeGi](https://arxiv.org/pdf/2305.03495)
- APE: execution accuracy (exact match) preferred over log-probability [P, via summary] — [APE](https://arxiv.org/html/2211.01910)
- GEPA: metric µ maps to [0,1]; feedback functions return text such as constraints satisfied/failed (IFBench), documents retrieved vs missing (HoVer/HotpotQA), and quality plus PII-leakage breakdown (PUPA) [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- IFBench uses automated Python verification functions and 58 out-of-distribution constraints [P, via summary; the summary's claims about "addressing verifier overfitting" were generic and are not relied on] — [IFBench](https://arxiv.org/pdf/2507.02833)
- PromptWizard: scoring via traditional metrics (e.g. F1) or an LLM evaluator; answer extraction and comparison are user-implemented per dataset [P/D] — [PromptWizard](https://arxiv.org/pdf/2405.18369), [README](https://github.com/microsoft/PromptWizard)
- AdalFlow: `AnswerMatchAcc(type="exact_match")` on numerical answers [D] — [AdalFlow docs](https://adalflow.sylph.ai/use_cases/question_answering.html)
- GEPA paper notes that, unlike earlier findings where instruction optimization helped mainly via quasi-exemplars (Wan et al., 2024), GEPA prompts contain declarative instructions, and reports a lower validation-test generalization gap [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- OPRO: training accuracy 5-20% above test (overfit gap acknowledged) [P, via summary] — [OPRO](https://arxiv.org/html/2309.03409)
- Explicit label-in-prompt (answer leakage) checks like AutoPrompter's "label absent from the prompt" filter: I found none in these papers/docs [absence of evidence in sources read].

### Inferences
- AutoPrompter's `contains` metric is looser than all of the above (substring + digit fallback + partial token credit). Exact match on short extractive spans, or a programmatic verifier, would match the literature; partial credit is what makes 0.13 -> 1.0 on train easy to reach by pasting answers.
- The label-not-in-prompt rule and max-3-words/no-digits filters are stronger than anything documented in the surveyed methods for leak prevention; but they only protect at dataset-build time, not against the optimizer later inserting training answers into the prompt (the observed 9/11). GEPA's remedy is to hide validation content from the optimizer and score a test set it never sees.

### Gaps
- No paper in the set measures metric gaming directly; the "known gameable" status of `contains` rests on AutoPrompter's own observation.

## 5. Output artifact per method

### Takeaway
Instruction-only (COPRO, OPRO, APE, ProTeGi, PromptAgent, EvoPrompt, TextGrad), instruction + demos (MIPROv2, PromptWizard, AdalFlow bootstrap), and candidate populations/Pareto sets (GEPA internally; most return one best).

### Cited Findings
- DSPy: few-shot optimizers produce demos from labelled data; instruction optimizers (MIPROv2, COPRO) produce instructions [D] — [optimizers.md](https://raw.githubusercontent.com/stanfordnlp/dspy/main/docs/docs/learn/optimization/optimizers.md)
- MIPROv2 jointly selects instructions and bootstrapped demos per module (default 4 bootstrapped + 4 labelled) [P/C] — [MIPRO](https://arxiv.org/pdf/2406.11695), [code](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/mipro_optimizer_v2.py)
- COPRO returns refined instructions and output-field prefixes only [C, via summary] — [copro_optimizer.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/copro_optimizer.py)
- GEPA maintains a Pareto front of candidates (best per training instance) and returns the candidate with the highest mean Dpareto score; optimized prompts are published in its appendix L [P] — [GEPA](https://arxiv.org/pdf/2507.19457)
- OPRO outputs natural-language instructions prepended to the question (GSM8K 80.2 vs 71.8 for "Let's think step by step") [P, via summary] — [OPRO](https://arxiv.org/html/2309.03409)
- ProTeGi: beam of prompts, final result by max-pooling over the final beam; textual "gradients" are intermediate [P] — [ProTeGi](https://arxiv.org/pdf/2305.03495)
- PromptAgent: MCTS over prompt states; output is the best prompt; reward from the held-out subset [P] — [PromptAgent](https://arxiv.org/pdf/2310.16427)
- EvoPrompt: population of prompts (size 10 in main experiments), the top dev-scoring prompt is reported [P] — [EvoPrompt](https://arxiv.org/pdf/2309.08532)
- TextGrad: single optimized prompt, accepted only if validation improves; baseline DSPy BFSR with 10 candidate programs and 8 few-shot examples [P] — [TextGrad](https://arxiv.org/pdf/2406.07496)
- PromptWizard: instruction + few-shot examples (some synthetic) + optional reasoning chains [P] — [PromptWizard](https://arxiv.org/pdf/2405.18369)
- AdalFlow: text-grad reached 89% and few-shot bootstrap 94% test accuracy on its documented example (vendor claim) [D] — [AdalFlow docs](https://adalflow.sylph.ai/use_cases/question_answering.html)

### Inferences
- AutoPrompter outputs an instruction prompt; inserting training answers into it is functionally the "demos" channel, but without demo-count caps or a demo/instruction separation, so memorization is unbounded. MIPROv2 caps demos (4+4) and tests them on a separate valset.

### Gaps
- Not verified: AdalFlow repo internals beyond docs; EvoPrompt/APE output details beyond the summary.

## 6. Where AutoPrompter is weaker, equal, or better

### Takeaway
Weaker on holdout size, selection/test separation, metric strictness, and leakage control at optimization time; arguably better on label provenance in grounded mode (verifiable against source text) and on dataset-build-time leak filters.

### Cited Findings (comparisons rest on facts above)
- Default mode: optimizer-synthesized eval from task description and no holdout. Even DSPy's weakest mode (GEPA with valset=None) warns about overfitting to the trainset [C] — [gepa.py](https://raw.githubusercontent.com/stanfordnlp/dspy/main/dspy/teleprompt/gepa/gepa.py)
- Standard published practice is a three-way split with a test set unseen by the optimizer (GEPA, MIPRO, TextGrad, PromptAgent, ProTeGi, PromptWizard) — see section 2 citations.

### Inferences
- Weaker: (1) tiny eval (about 11 train labels); (2) no never-touched test split if the 2:1 holdout also selects; (3) lenient `contains` metric; (4) the optimizer sees training labels and can paste them (GEPA hides validation content; MIPRO limits demos); (5) the default mode has no independent labels; (6) labels are LLM-written (Opus), unlike human-labelled benchmarks, and the extractive 1-3 word filter biases toward lookup tasks.
- Equal: 2:1 split ratio is in the usual range (GEPA is about 1:2 train:val, TextGrad 50/100/100, PromptAgent about half held for test); grounded extractive labels give verifiable correctness similar in spirit to programmatic verifiers (IFBench) or exact match.
- Better: the label-absent-from-prompt and verbatim-in-source filters at dataset creation are more explicit leak controls than any documented in the surveyed methods; per-run regeneration is a drawback in default mode but the `reuse_dataset` option (latest commit) addresses comparability.
- Suggested next checks (not in sources): scale the grounded set to >=100 items; add an untouched test split; report holdout CI; switch to exact match or normalized-token F1 with no partial credit; reject prompt candidates containing any training label string (n-gram overlap check).

### Gaps
- No source quantifies how much holdout size is needed for a given effect; the sample-size suggestions above are the researcher's inference, not cited.
