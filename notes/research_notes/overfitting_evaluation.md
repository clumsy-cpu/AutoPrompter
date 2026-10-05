# Overfitting, memorization, metric gaming and evaluation validity in automatic prompt optimization

Evidence-grade tags: [PR] peer-reviewed venue; [PP] arXiv preprint, not peer reviewed; [DOC] vendor/framework docs; [BLOG] blog/aggregator. No third-party independent reproduction of overfitting claims was found for any item unless stated. Tool note: several pages were read via a small-model summarizer; numbers below were verified against full text only where marked (full-text).

## 1. Documented overfitting / label leakage and train-vs-test gaps

### Takeaway
Overfitting to small training sets is documented in the original OPRO paper, MIPROv2, and a recent GEPA re-implementation study (a 28-point regression below the seed prompt at Ntrain=30). Direct evidence of a rewriter copying training answers into the prompt exists for MIPROv2 (instructions overfit to the meta-prompt's few-shot examples) and for an unconstrained guideline writer (reference-answer enforcement). Our failure mode (lookup table of 9/11 answers) matches these.

### Cited Findings
- OPRO (Google DeepMind) reports training accuracies "often 5%-20% higher than test accuracies" yet still mostly above human prompts; it deliberately used no validation set by default, argues overfitting is benign when all candidates overfit similarly, and suggests a larger training set and early stopping to reduce it [PP/ICLR 2024] — [HackerNoon summary of OPRO](https://hackernoon.com/how-overfitting-affects-prompt-optimization); paper: [arXiv 2309.03409](https://arxiv.org/pdf/2309.03409). (Summary-level read; OPRO PDF not directly verified.)
- MIPROv2 paper states a failure mode of its proposers: "the tendency to overfit instructions to the few-shot examples provided in the meta-prompt"; such instructions sometimes end up in the best programs, which the authors hypothesize act as few-shot examples; left to future work (full-text) — [MIPRO paper appendix](https://arxiv.org/abs/2406.11695) [PR, EMNLP 2024]. (Paper ID taken from known citation; text read from a local PDF copy.)
- MAGE study (single-author preprint, 2607.11944): re-implemented GEPA, gpt-4o-mini, GSM8K-Hard, Ntrain=30, Ntest=50, 5 seeds. GEPA-optimized prompts scored 34.0% on test vs 62.4% for the unoptimized seed (a -28.4 point regression); the author says "reflective optimization can overfit small training sets severely" and attributes it to clustered failures dominating the reflection trace (full-text). OPRO and Self-Refine returned the seed prompt unchanged on all seeds. A fixed CoT-math prompt got 70.0% with no optimization; MIPROv2+CoT went 71.1% -> 68.9%. In low-data regimes (Ntrain=30) "well-designed fixed prompts outperform all reflective optimizers" — [MAGE arXiv](https://arxiv.org/pdf/2607.11944) [PP]. Caveats: one author, one task family, Ntest=50 (2% per question), re-implementation of GEPA not the official library.
- Wan et al. (NeurIPS 2024): optimized exemplars generalize better than optimized instructions; validation-test generalization gaps are smaller for exemplar optimization in all cases studied; they call for "regularization and cross-validation in APO" as analogues to classical ML (full-text) — [Teach Better or Show Smarter, arXiv 2406.15708](https://arxiv.org/pdf/2406.15708v2) [PR].
- GEPA paper: re-did Wan et al.'s generalization-gap analysis (Fig. 16) and reports reflectively evolved instructions have a lower generalization gap (val vs test) than earlier IO methods; no train-vs-test overfitting quantification beyond that (full-text) — [GEPA arXiv 2507.19457](https://arxiv.org/pdf/2507.19457v2) [PR, ICLR 2026 status unknown].
- AGOPS (guideline evolution preprint): an unconstrained prompt writer can "find guidelines to enforce the reference answer", coinciding with higher prompt-answer overlap (search-snippet level only; mechanism of the paper's own prevention not retrieved) — [arXiv 2607.14105](https://arxiv.org/abs/2607.14105) [PP]; snippet via search, treat as lower confidence.
- LangChain's blog experiments on prompt optimizers note "the lower bound for most of the experiments is negative – the current settings sometimes cause the prompt to overfit"; best case ~200% relative gain, some configs degraded — [LangChain blog](https://www.langchain.com/blog/exploring-prompt-optimization) [BLOG].

### Inferences
- Pasting training answers into the prompt is the extreme end of MIPRO's documented "instructions overfit to the examples shown to the proposer"; it will always drive train to 1.0 while holdout stays near baseline, as observed (0.27 -> 0.40 is within noise at n=5).
- With 5 holdout items, one item = 0.2; the 0.27->0.40 change is likely 1 question (or partial credit) and not evidence of generalization.

### Gaps
- No paper found that explicitly measures "fraction of training labels verbatim in the final prompt"; no standard n-gram-overlap leakage benchmark for APO located.
- No independent reproduction of the MAGE -28.4 point GEPA result; official GEPA behavior at Ntrain=30 on that task is unknown.

## 2. Proven mitigations

### Takeaway
The established defenses are structural: a held-out valset used only for candidate selection and never shown to the reflector (GEPA), minibatch evaluation plus full-valset scoring (MIPRO), Pareto/diversity selection, short prompts, and plain train/val/test splits. None directly blocks verbatim answer pasting; no peer-reviewed n-gram leakage filter was found.

### Cited Findings
- GEPA protocol: optimizers get full access to the train split including labels; validation instances are only used for scoring (early-stopping style), "direct access to the content of validation instances is restricted" (full-text). Algorithm splits Dtrain into Dfeedback and Dpareto, reflects on minibatches from Dfeedback, and returns the candidate with highest average score on Dpareto — [GEPA arXiv](https://arxiv.org/pdf/2507.19457v2) [PR]; DSPy docs confirm reflection uses execution traces and feedback from train minibatches, not valset — [DSPy GEPA docs](https://raw.githubusercontent.com/stanfordnlp/dspy/main/docs/docs/api/optimizers/GEPA/overview.md) [DOC].
- GEPA's final prompts are up to 9.2x shorter than MIPROv2's, and the paper lists reduced prompt size as a practical advantage (full-text) — [GEPA arXiv](https://arxiv.org/pdf/2507.19457v2). Note GEPA paper has no ablation of Pareto vs best-candidate selection on generalization in the text I could extract.
- MIPROv2 in DSPy: if no valset is given, 80% of trainset is also used as validation to score candidates; docs suggest 50-500 examples — [DSPy MIPROv2 API (search snippet)](https://dspy.ai/api/optimizers/MIPROv2/) [DOC]. MIPRO uses minibatch scoring (Algorithm: "Minibatch size B") with periodic full evaluation — [MIPRO paper](https://arxiv.org/abs/2406.11695) [PR].
- Opik docs: 70-80% train / 20-30% validation, optional untouched test set, keep splits immutable and distributions consistent — [Opik dataset docs](https://www.comet.com/docs/opik/development/optimization-runs/optimization/define_datasets.md) [DOC].
- Few-shot demos vs instruction: Wan et al. find exemplar optimization generalizes with smaller gaps, and combining IO+EO is best; LangChain blog: few-shot suits nuanced preference/in-domain tasks, instruction optimization suits discovering hidden rules — [Wan et al.](https://arxiv.org/pdf/2406.15708v2) [PR]; [LangChain](https://www.langchain.com/blog/exploring-prompt-optimization) [BLOG].
- MAGE: multi-objective Pareto selection with a token-length objective and episodic memory partially mitigated overfitting (46.4% vs GEPA 34.0%), but still below the fixed CoT prompt (70.0%) and with high variance (n=5 candidates: +/-17.5%) — [MAGE](https://arxiv.org/pdf/2607.11944) [PP].
- OPRO suggests larger training set and fewer steps (early stopping) — [HackerNoon/OPRO](https://hackernoon.com/how-overfitting-affects-prompt-optimization).

### Inferences
- For our setup: (a) a true holdout/valset for selecting the final prompt, disjoint from examples the optimizer sees, with reporting of best-val not best-train; (b) never expose train labels verbatim to the rewriter without a copy guard, or expose only failure feedback; (c) a post-hoc check rejecting candidates whose n-gram overlap with training answers exceeds a threshold is a reasonable engineering fix but is unproven in literature (my suggestion, uncited); (d) length/diff regularization (reject large deletions of untested sections) mirrors Pareto-with-length in MAGE.
- Seeing only failing training examples (our setup) matches GEPA's feedback-minibatch design but amplifies "clustered failures dominate reflection" risk noted by MAGE.

### Gaps
- No source quantifying n-gram overlap/leakage guards or "forbid pasting answers" meta-prompt constraints' effectiveness.
- Cross-validation in APO: Wan et al. only recommend it as future work; no implementation evidence found.
- Early-stopping efficacy for APO: only OPRO's suggestion; no controlled study found.

## 3. Metric design and reward hacking

### Takeaway
Reward hacking of proxy metrics is documented for LLM judges and, in a theory-oriented preprint, for prompt optimization specifically. Lenient string metrics are a form of the same weakness; no APO-specific empirical study of `contains`-style metrics was found.

### Cited Findings
- "Optimizing the Score, Losing Sight of the Task" (preprint, 19 pages): treats persistent prompts as a substrate for reward hacking; "measured progress can conceal unchanged or deteriorating task performance"; recommends controlling accessible failure modes and preserving evidence of task quality independent of the optimized score — [arXiv 2609.25848](https://arxiv.org/abs/2609.25848) [PP]; (abstract-level read; no empirical numbers retrieved).
- LLM judges are exploitable: superficial "master key" inputs yield false-positive rates up to 80% — [One Token to Fool LLM-as-a-Judge, NeurIPS 2025](https://nips.cc/virtual/2025/131135) [PR] (search snippet). Another preprint: self-play moved a judge's pass rate 0.72 -> 0.94 while true accuracy stayed 0.20 — [arXiv 2609.02246](https://arxiv.org/pdf/2609.02246) [PP] (snippet only).
- GEPA/DSPy guidance: use feedback metrics returning score plus text feedback grounded in automatic validators (tests, schemas) or LLM judges — [DSPy GEPA docs](https://raw.githubusercontent.com/stanfordnlp/dspy/main/docs/docs/api/optimizers/GEPA/overview.md) [DOC].
- Underspecification: AGOPS reports prompt underspecification drops performance up to 95.3% and that reference answers implicitly carry missing information, so optimizers push them into the prompt — [arXiv 2607.14105](https://arxiv.org/abs/2607.14105) [PP].

### Inferences
- Our `contains` metric with digit fallback is a lenient proxy the optimizer can satisfy with "never refuse, guess" plus pasted answers; stricter metrics (exact/normalized match, refusal detection, answer-must-not-be-in-prompt check) close the observed hole. Not directly supported by a cited study.

### Gaps
- No study comparing exact match vs lenient matching in APO outcomes was found.
- Judge-bias evidence found is for RL/reward settings, not prompt-optimization loops.

## 4. Minimum dataset sizes

### Takeaway
DSPy guidance: ~10 examples only for BootstrapFewShot; 50+ for random search; 200+ for MIPROv2 "to prevent overfitting". 11 train / 5 holdout is below every documented threshold.

### Cited Findings
- "very few examples (around 10) -> BootstrapFewShot; 50 or more -> BootstrapFewShotWithRandomSearch; 200 examples or more to prevent overfitting -> MIPROv2 (40+ trials)" — [DSPy optimizers doc](https://raw.githubusercontent.com/stanfordnlp/dspy/main/docs/docs/learn/optimization/optimizers.md) [DOC]. No count given for GEPA there.
- MIPROv2 API: 50-500 examples recommended for optimization — [DSPy MIPROv2 API](https://dspy.ai/api/optimizers/MIPROv2/) [DOC] (snippet).
- MAGE: Ntrain=30 is below the threshold where reflective optimization beats fixed prompts; "future work should identify the Ntrain threshold" — [MAGE](https://arxiv.org/pdf/2607.11944) [PP].
- GEPA benchmarks used e.g. HoVer 150 train / 300 val / 300 test; LiveBench-Math 368 questions split equally — [GEPA appendix](https://arxiv.org/pdf/2507.19457v2) [PR].

### Inferences
- Minimal credible evaluation here is probably >=30-50 holdout items; with n=5 the standard error on accuracy is ~20 points (basic binomial arithmetic).

### Gaps
- No ablation sweeping train size for GEPA found; official GEPA minimum unknown.

## 5. Independent / third-party comparisons

### Takeaway
Independent evidence is thin and mostly mixed: little reproduction of GEPA/MIPRO headline numbers; the available independent-ish studies find optimized prompts often fail to transfer and fixed prompts frequently match them.

### Cited Findings
- Survey: "A Systematic Survey of Automatic Prompt Optimization Techniques", EMNLP 2025, pp. 33066-33098 — [arXiv 2502.16923](https://arxiv.org/abs/2502.16923) [PR]. I only retrieved the abstract; whether it discusses overfitting/evaluation validity is unknown.
- "Why Prompt Optimization Works, and Why It Sometimes Doesn't" (preprint 2605.26655): analyses DSPy-MIPROv2 (2,095 pairwise comparisons) and TextGrad/GEPA (17,708) across 11 benchmarks and several backbones; optimized-prompt superiority on one benchmark often fails to transfer; complexity-increasing/meta-instruction edits hurt math and multi-hop; only 2 of 60 tests survive FDR correction — [alphaXiv](https://www.alphaxiv.org/abs/2605.26655.md) [PP, third-party, secondary summary].
- MAGE (above) is a third-party re-implementation of GEPA/OPRO/Self-Refine/MIPROv2 — [arXiv 2607.11944](https://arxiv.org/pdf/2607.11944) [PP].
- "Revisiting Automated Prompting: Are We Actually Doing Better?" (Zhou et al.): manual prompts best in 13/24 setups; but uses RoBERTa-large with older methods (AutoPrompt), limited relevance to LLM optimizers — [summary](https://liner.com/review/revisiting-automated-prompting-are-we-actually-doing-better) [BLOG, venue/ID not verified].
- A "prompt optimizer comparison" on benchlm.ai is vendor-authored (conflict of interest) and about consumer rewriting tools; not used.

### Inferences
- Treat headline gains from GEPA/MIPRO as vendor/author-reported until independently reproduced; "how many results were reproduced" is essentially unknown.

### Gaps
- No systematic reproducibility study of DSPy/TextGrad/GEPA/OPRO found; survey 2502.16923's evaluation-validity content not read.

## 6. Can prompt optimization teach facts the model lacks?

### Takeaway
Optimization can only elicit or format knowledge the model has, or inject facts by literally embedding them in the prompt (context stuffing), which does not generalize to unseen questions. This explains train 1.0 / holdout flat.

### Cited Findings
- A domain-knowledge-injection survey classes prompt optimization as using the model's internal knowledge and "fundamentally limited by the knowledge already present in the model"; long prompts also consume context — [Injecting Domain-Specific Knowledge into LLMs: survey, arXiv 2502.10708](https://arxiv.org/pdf/2502.10708) [PP/survey, snippet-level].
- Instruction optimization can discover hidden patterns/rules not in the model's training data (~3x accuracy in discovery-heavy tasks), but this is rule discovery from examples, not fact memorization — [LangChain blog](https://www.langchain.com/blog/exploring-prompt-optimization) [BLOG].
- AGOPS: reference answers encode missing task information that optimizers pull into prompts; evolved guidelines recovered 15.5-81.7% on underspecified tasks — [arXiv 2607.14105](https://arxiv.org/abs/2607.14105) [PP].

### Inferences
- If answers depend on facts in the (long) skill document that the target cannot see or retrieve, the optimizer can only (a) paste answers (overfit) or (b) induce guessing; holdout gain would be ~chance. A legitimate fix is supplying the relevant document context (retrieval) rather than letting the optimizer compress it.

### Gaps
- No controlled study of fact-vs-instruction optimization with held-out questions found; "knowledge vs instruction" evidence is indirect.
