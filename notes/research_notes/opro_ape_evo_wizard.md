# Search / evolutionary prompt optimizers: OPRO, APE, EvoPrompt, PromptAgent, PromptWizard

Evidence labels: [PR] = peer-reviewed venue paper; [PP] = preprint only; [CODE] = read directly from the cloned repo at the commit noted; [README] = repo README claim only. Repos were cloned at depth 1 on 2026-10-05 (default branch `main` in all five). Paper numbers come from the full arXiv PDFs (text-extracted), not from search snippets.

Venues: OPRO = ICLR 2024 [PR] ([ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/3339f19c5fcee3ad74502947a32be9e6-Abstract-Conference.html)); APE = ICLR 2023 [PR] (PDF header "Published as a conference paper at ICLR 2023", [arXiv 2211.01910](https://arxiv.org/abs/2211.01910)); EvoPrompt = ICLR 2024 [PR] ([arXiv 2309.08532](https://arxiv.org/abs/2309.08532), PDF header; [repo README](https://github.com/beeevita/EvoPrompt)); PromptAgent = ICLR 2024 [PR] ([repo README](https://github.com/XinyuanWangCS/PromptAgent), "accepted by ICLR 2024"); PromptWizard = Findings of ACL 2025 [PR] ([ACL Anthology 2025.findings-acl.1025](https://preview.aclanthology.org/new-sigs/2025.findings-acl.1025/); the arXiv v2 [2405.18369](https://arxiv.org/abs/2405.18369) is what I read, and its numbers may differ from the camera-ready).

## 1. Loop structure (per system)

### Takeaway
OPRO is a single-trajectory loop that shows the optimizer the top-20 (instruction, score) pairs sorted ascending plus 3 exemplars and samples 8 candidates per step. APE is mostly one-shot propose-then-score (iterative resampling exists in the paper but is not in the public code). EvoPrompt is population-based (10 prompts x 10 generations, GA or DE operators executed by an LLM). PromptAgent is MCTS over prompt "states" with error-feedback "gradients". PromptWizard is a fixed pipeline of mutate / score / critique / synthesize on instructions, then on examples, with about 69 LLM calls total.

### Cited Findings

**OPRO**
- Each step: the optimizer LLM is called with a meta-prompt; new solutions are scored and added back into the meta-prompt for the next step. — [OPRO abstract, arXiv 2309.03409](https://arxiv.org/pdf/2309.03409)
- Meta-prompt has two parts: (a) past instructions with training accuracies; (b) a problem description with several exemplars randomly picked from the training set, plus meta-instructions (e.g. "Write your new text that is different from the old ones and has a score as high as possible", output in square brackets). — [arXiv 2309.03409 s2.2, s4.2, Fig. 3](https://arxiv.org/pdf/2309.03409)
- The trajectory is "sorted in the ascending order" by score (best last), and "we only keep instructions with the highest scores in the meta-prompt" because of context length. — [arXiv 2309.03409 s2.2, s4.2](https://arxiv.org/pdf/2309.03409)
- Multiple candidates per step is explicitly motivated as an optimization-stability measure: "we prompt the LLM to generate multiple solutions at each optimization step". Default: 8 instructions per step, optimizer temperature 1.0, scorer temperature 0 (greedy), meta-prompt holds the best 20 instructions and 3 randomly picked exemplars, default 200 steps. — [arXiv 2309.03409 s2.3, s5.1](https://arxiv.org/pdf/2309.03409)
- Ablation on candidates per step (1/2/4/8/16): 8 per step "overall achieves the best performance". — [arXiv 2309.03409 s5.3, Fig. 8](https://arxiv.org/pdf/2309.03409)
- Exemplar choice: random, or "the ones the previous instructions fall short of" (error cases). The paper reports results with error exemplars "are similar, indicating that the error cases alone are not informative enough" and lists richer error feedback as future work. — [arXiv 2309.03409 s4.2, Limitations](https://arxiv.org/pdf/2309.03409)
- Ablation: one-shot generation of 50 instructions from the same meta-instructions (no trajectory) is much worse. Best of 50 on GSM8K: train 64.4 / test 60.8, versus OPRO's "Let's do the math!" at step 5, train 78.2 / test 76.3. — [arXiv 2309.03409 App. (one-step generation ablation)](https://arxiv.org/pdf/2309.03409)
- Code details [CODE]: duplicates are rejected by md5 hash of the instruction text (`old_instruction_md5_hashstrings_set`); candidates >500 chars, containing "INS", or (for GSM8K) containing digits are skipped; `max_num_instructions=20`, `num_score_buckets=100` (scores shown to the optimizer as integers 0-100), `old_instruction_score_threshold` (0.15 for GSM8K in a comment, 0.3 for others) drops very low scorers from the meta-prompt; `few_shot_selection_criteria` in {random, constant, current_most_frequent, accumulative_most_frequent} (the last two put the most-often-wrong training questions in the meta-prompt). — [opt_utils.py](https://github.com/google-deepmind/opro/blob/main/opro/optimization/opt_utils.py), [optimize_instructions.py](https://github.com/google-deepmind/opro/blob/main/opro/optimization/optimize_instructions.py)

**APE**
- Algorithm 1: sample instruction proposals U with an LLM; loop: pick a random training subset, score every candidate on it, keep the top k%, then either keep U_k or LLM-resample variants of U_k ("Generate a variation of the following instruction while keeping the semantic meaning"). Return the argmax on the full training data. — [arXiv 2211.01910 s3, Alg. 1, Fig. 3](https://arxiv.org/pdf/2211.01910)
- Proposal modes: "forward" (the LLM completes an instruction given demos) and "reverse" (fill-in-the-blank/insert mode). Scoring: execution accuracy (0-1 loss) or log-probability of the target. — [arXiv 2211.01910 s3.1-3.2](https://arxiv.org/pdf/2211.01910)
- Adaptive filtering: score all candidates on a small subset, re-score survivors on new non-overlapping subsets (moving average), full-set evaluation only for the few left. — [arXiv 2211.01910 s3.2](https://arxiv.org/pdf/2211.01910)
- Iterative Monte Carlo search improved the proposal set but "the highest scoring instruction tends to remain the same"; the authors conclude it gives "marginal improvement" and use APE without iterative search by default. — [arXiv 2211.01910 s3.3](https://arxiv.org/pdf/2211.01910)
- Setup for Instruction Induction: 5 input-output pairs sampled from training data for proposal; default 50 sampled instructions (64 reached human level); 5 seeds. — [arXiv 2211.01910 s4, s5.2](https://arxiv.org/pdf/2211.01910)
- Public code [CODE]: `find_prompts` = generate prompts (`num_subsamples` x `num_demos`=5 demos x `num_prompts_per_subsample`), de-duplicate with `set()`, then score with a UCB bandit (`bandits.yaml`: `bandit_method: ucb`, `c: 1.0`, `rounds: 5`, `num_prompts_per_round: 50`, `num_samples: 50`). There is no resampling loop in the repo (grep for "resample"/"iterative" over the package returns nothing). `experiments/run_instruction_induction.py` splits the induce data into `prompt_gen_data` and `eval_data` (3 subsamples x 30 prompts, eval on up to 20 examples), then reports the top prompt on the separate test set (100 examples). — [ape.py](https://github.com/keirp/automatic_prompt_engineer/blob/main/automatic_prompt_engineer/ape.py), [bandits.yaml](https://github.com/keirp/automatic_prompt_engineer/blob/main/automatic_prompt_engineer/configs/bandits.yaml), [run_instruction_induction.py](https://github.com/keirp/automatic_prompt_engineer/blob/main/experiments/run_instruction_induction.py)

**EvoPrompt**
- Algorithm: initial population P0 of N prompts scored on a dev set D; for T iterations: select parents, `Evo(.)` produces a child via an LLM, evaluate it on D, update the population; return argmax of the final population. — [arXiv 2309.08532 Alg. 1](https://arxiv.org/pdf/2309.08532)
- GA: roulette-wheel selection of two parents (tournament and random tried in Table 4, roulette best); the LLM is told to crossover the two prompts and then mutate the result. Survivor update: N new children merged with the old population, top N kept. — [arXiv 2309.08532 s3.2, Table 4](https://arxiv.org/pdf/2309.08532)
- DE: for each prompt p_i, the LLM finds the differing parts of two random prompts, mutates them, merges with the current best prompt, then crosses over with p_i; keep the better of p_i and the child (population size constant). — [arXiv 2309.08532 s3.3, Fig. 2](https://arxiv.org/pdf/2309.08532)
- Initial population is human-written/APE prompts, paraphrased, not random. — [arXiv 2309.08532 s3.1](https://arxiv.org/pdf/2309.08532)
- Hyperparameters (Table 11): population 10, steps 10; dev set 200 (classification, Alpaca-7b), 100 (generation), 50 (BBH, GPT-3.5, 3-shot). Evolution LLM temperature 0.5 for GPT-3.5. — [arXiv 2309.08532 App. B.3, Table 11](https://arxiv.org/pdf/2309.08532)
- Code [CODE]: `GAEvoluter.evolute` in `evoluter.py` keeps `evaluated_prompts` (a dict prompt -> scores, so repeated prompts are not re-scored), supports `ga_mode` std/topk and `sel_mode` wheel/tour/random; `--budget` (default 10) and `--popsize` (default 10) in `args.py`. GA operator text lives in `data/template_ga.py`. — [evoluter.py](https://github.com/beeevita/EvoPrompt/blob/main/evoluter.py), [args.py](https://github.com/beeevita/EvoPrompt/blob/main/args.py), [template_ga.py](https://github.com/beeevita/EvoPrompt/blob/main/data/template_ga.py)

**PromptAgent**
- Formulation: state = a prompt version, action = an edit derived from model-error feedback, reward = task score on a held-out set separate from the training samples; MCTS with selection (UCT), expansion, simulation, back-propagation. — [arXiv 2310.16427 s3.1-3.2](https://arxiv.org/pdf/2310.16427)
- Expansion: sample `expand width` minibatches (batch size 5) from the training set; for each, the base model answers, wrong examples are collected, the optimizer LLM writes an error analysis ("gradient"), then writes `num samples` new prompts conditioned on current prompt + errors + the trajectory of ancestor prompts. Each child is scored on the held-out reward set. — [arXiv 2310.16427 App. A.3](https://arxiv.org/pdf/2310.16427); [gradient_descent_prompts.py](https://github.com/XinyuanWangCS/PromptAgent/blob/main/src/prompt_optim_agent/world_model/prompts/gradient_descent_prompts.py) [CODE] (template adapted from ProTeGi/APO, per the file's own header comment)
- Hyperparameters: 12 MCTS iterations, UCT exploration weight c=2.5, optimizer GPT-4 at temperature 1.0, base GPT-3.5 at 0.0. Settings Standard (depth 8, width 3, 1 sample), Wide (depth 6, width 3, 2 samples), Lite (depth 4, width 3, 1 sample). Early stopping after depth>2 using min/max reward thresholds. — [arXiv 2310.16427 s4, App. A.3, Table 7](https://arxiv.org/pdf/2310.16427)
- Repo's `example_config.yaml` default: `iteration_num: 10`, `expand_width: 3`, `depth_limit: 5`, `w_exp: 2.5`, `train_batch_size: 5`, `train_size 70 / eval_size 50 / test_size 79`; also a `beam_search` alternative. — [example_config.yaml](https://github.com/XinyuanWangCS/PromptAgent/blob/main/example_config.yaml) [CODE]
- Search-algorithm ablation (Table 4): MC < Greedy < Beam < MCTS at matched budget (average 0.635 / 0.697 / 0.698 / 0.754 for MC / Greedy / Beam / PromptAgent in the extracted table; column alignment of the extracted text is slightly ambiguous, see Gaps). — [arXiv 2310.16427 s5.2, Table 4](https://arxiv.org/pdf/2310.16427)

**PromptWizard**
- Pipeline: (1) mutate with predefined "thinking styles" in one LLM call; score on mini-batches of 5 training examples; critique the best prompt using failing examples; synthesize an improved prompt. (2) Select diverse positive/negative examples from 25 random candidates (about 5 iterations). (3) Sequential optimization of instruction and few-shot examples with critique/synthesize, generating synthetic examples. (4) Self-generated chain-of-thought reasoning plus validation. (5) Task intent and expert-persona integration. — [arXiv 2405.18369 s3](https://arxiv.org/pdf/2405.18369)
- Hyperparameters in paper: mutated prompts and mutation rounds 3, diverse examples 25, sequential optimization rounds 5, only 25 training examples, results averaged over 3 runs, GPT-3.5-Turbo or GPT-4 for all components. — [arXiv 2405.18369 s4](https://arxiv.org/pdf/2405.18369)
- Cost breakdown: 69 API calls per task (48 prompt refinement, 5 example selection, 12 sequential optimization, 4 reasoning/validation/intent/expert). — [arXiv 2405.18369 s5.2](https://arxiv.org/pdf/2405.18369)
- Code [CODE]: `core_logic.py` (`gen_different_styles`, `get_prompt_score`, `critique_and_refine`, `refine_prompts`, `select_top_prompts`, `generate_best_examples`, `get_best_prompt`). Config knobs: `mutate_refine_iterations: 3`, `mutation_rounds: 3`, `refine_task_eg_iterations: 3`, `style_variation: 5`, `questions_batch_size: 1`, `min_correct_count: 3`, `max_eval_batches: 6`, `top_n: 1`, `seen_set_size: 25`, `few_shot_count: 5`, `num_train_examples: 20`, `generate_reasoning`, `generate_expert_identity`. — [core_logic.py](https://github.com/microsoft/PromptWizard/blob/main/promptwizard/glue/promptopt/techniques/critique_n_refine/core_logic.py), [gsm8k promptopt_config.yaml](https://github.com/microsoft/PromptWizard/blob/main/demos/gsm8k/configs/promptopt_config.yaml)
- Scoring in code is very coarse [CODE]: for each candidate, `get_prompt_score` draws `questions_batch_size` (default 1) random training questions, asks the LLM, and stops at the first failing batch or after `max_eval_batches` (6); the score is `correct_count/count`, so a prompt is judged on at most about 6 questions. — [core_logic.py `get_prompt_score`](https://github.com/microsoft/PromptWizard/blob/main/promptwizard/glue/promptopt/techniques/critique_n_refine/core_logic.py)
- Three scenarios: no data, synthetic examples, or training data. — [README](https://github.com/microsoft/PromptWizard)

### Inferences
- OPRO's candidate-per-step (8) and sorted top-20 history are what make its single trajectory stable; our single-candidate loop loses both the variance reduction and the "similarities among high scorers" signal.
- OPRO already has the duplicate-rejection ledger (md5 of instruction); that part of our design matches OPRO, not something new.
- APE's public code is not an iterative optimizer; for a loop comparison it is best treated as a "generate N, score, pick best" baseline.

### Gaps
- OPRO's total number of LLM calls per run is not stated in the paper text I extracted; derived estimate only: 200 steps x 8 = 1,600 scored instructions, each scored on a training subset (3.5% of 7,473 GSM8K train = about 260 examples; my arithmetic, not the paper's).
- PromptAgent's per-run LLM-call total is not stated; only counts of explored prompts (Greedy-S 34, Greedy-L 72, APE 150) in Fig. 4a. — [arXiv 2310.16427 App. A.3](https://arxiv.org/pdf/2310.16427)
- Table 4 (PromptAgent search ablation) column mapping not fully verified from the PDF text extraction.

## 2. Feedback type used

### Takeaway
OPRO and EvoPrompt use only scalar scores (no per-example failure text by default). APE uses scalar scores only. PromptAgent and PromptWizard feed failing examples to an LLM that writes an error analysis/critique. Our system (history + failure feedback) is a hybrid of OPRO-style history and PromptAgent-style error feedback.

### Cited Findings
- OPRO: aggregate training accuracy per instruction; the paper says "richer feedback about the error cases besides the aggregated accuracy" is a promising direction. — [arXiv 2309.03409 Limitations](https://arxiv.org/pdf/2309.03409)
- APE: scalar execution accuracy or log-probability; no error text. — [arXiv 2211.01910 s3.2](https://arxiv.org/pdf/2211.01910)
- EvoPrompt: dev-set score as fitness only; the LLM does crossover/mutation on prompt text without seeing errors. The authors contrast this with approaches that use "predicted samples" feedback. — [arXiv 2309.08532 s1-s3](https://arxiv.org/pdf/2309.08532)
- PromptAgent: error feedback from wrong minibatch examples; optimizer writes reasons then new prompt; the template is explicitly adapted from the gradient-descent prompts of APO/ProTeGi (arXiv 2305.03495). — [gradient_descent_prompts.py](https://github.com/XinyuanWangCS/PromptAgent/blob/main/src/prompt_optim_agent/world_model/prompts/gradient_descent_prompts.py) [CODE]; [arXiv 2310.16427](https://arxiv.org/pdf/2310.16427)
- PromptWizard: LLM critique of the best prompt using failing examples, then synthesis; positive and negative examples both used. — [arXiv 2405.18369 s3.1-3.3](https://arxiv.org/pdf/2405.18369)

### Inferences
- PromptAgent's feedback template also puts raw wrong examples (question, model response, label) in the optimizer prompt. If AutoPrompter does the same with training items, that is a direct route for "memorizing answers into the prompt"; none of the five systems' code asks the optimizer to avoid copying example answers (I did not find such a guard in the templates I read; only OPRO's meta-instruction "concise and generally applicable" in the paper).

### Gaps
- Did not check whether PromptWizard's critique prompts forbid answer leakage (prompt_pool.yaml not read in full).

## 3. Anti-overfitting: subset sizes, held-out reporting, train/test gaps

### Takeaway
All five report on a separate test set, and OPRO, PromptAgent and APE's code score candidates on a small training/held-out subset rather than all data. OPRO explicitly runs without a validation set by default and reports 5-20 point train-over-test gaps. Only PromptAgent and APE's experiment script separate an eval/reward split from the examples used to generate feedback or proposals. EvoPrompt's BBH dev set is sampled from the test set.

### Cited Findings
- OPRO: scoring on small train fractions: 3.5% of GSM8K train, 20% of each BBH task; the rest of BBH is test. "For simplicity, we do not set aside a validation set in our default setting." — [arXiv 2309.03409 s4.1, s5.1, s5.4](https://arxiv.org/pdf/2309.03409); code `train_ratio=0.035 / eval_ratio=0` (gsm8k), `0.2 / 0` (bbh), `0.8 / 0.2` (mmlu) [CODE: optimize_instructions.py](https://github.com/google-deepmind/opro/blob/main/opro/optimization/optimize_instructions.py)
- OPRO overfitting analysis: with a 1/3-1/3-1/3 train/val/test split, validation curves "trend up and down alongside the training curves"; but "in Table 7 and 10, our training accuracies are often 5%-20% higher than our test accuracies". Mitigations suggested: larger training set, early stopping. Rule of thumb: training set should have "at least tens of samples" so the prompt "does not severely overfit". — [arXiv 2309.03409 s5.4, Limitations](https://arxiv.org/pdf/2309.03409)
- OPRO code can compute validation accuracy of each generated instruction every `eval_interval=3` steps if `eval_ratio>0`; it is off by default for GSM8K/BBH. — [optimize_instructions.py, opt_utils.py](https://github.com/google-deepmind/opro/blob/main/opro/optimization/opt_utils.py) [CODE]
- APE: 5 demos for proposal; candidates scored on small random subsets then more data; Instruction Induction test uses separate eval data; the authors note instructions selected by zero-shot accuracy "overfit the zero-shot learning scenario" and hurt few-shot on Rhymes, Large Animal, Second Letters. TruthfulQA: 100 train / 717 test, "top 10 of 200 candidates on the training set generalizes well". They also note APE can "hack the evaluation" with degenerate answers on some tasks. — [arXiv 2211.01910 s4, s4.3, App.](https://arxiv.org/pdf/2211.01910)
- EvoPrompt: pick the best prompt by dev score, report on test; dev set 200/100/50; for BBH "We sample a subset from the test set as the development set". No overfitting analysis found in the text (grep for overfit/generaliz returned only reference-list hits). GPT-3.5 results use a single seed ("budget limitation"); Alpaca results average 3 seeds. — [arXiv 2309.08532 s4.1, s4.4, Table 11](https://arxiv.org/pdf/2309.08532)
- PromptAgent: reward is computed on a separate held-out subset (default 150, range 60-200) of the training data, distinct from the batches used to elicit error feedback and from the test set. Table 6 gives train/test sizes per task, e.g. Penguins 70/79, Epistemic 500/500, NCBI 2000/940. Fig. 4b plots training (reward) and test accuracy vs depth for Epistemic; both rise then stabilize after depth 3. The text says transfer across base models "varies" (PaLM 2 beat baselines on 7/12 tasks). — [arXiv 2310.16427 s3.1, App. A.2, Table 6, s5.2, Table 3](https://arxiv.org/pdf/2310.16427)
- PromptWizard: only 25 training examples (or 5 in a low-resource experiment); evaluation on the full test set; no validation split described; scoring uses at most about 6 random training questions per candidate in code. — [arXiv 2405.18369 s4, s6](https://arxiv.org/pdf/2405.18369); [core_logic.py](https://github.com/microsoft/PromptWizard/blob/main/promptwizard/glue/promptopt/techniques/critique_n_refine/core_logic.py) [CODE]
- Independent report (preprint): OPRO "shows limited effectiveness in small-scale LLMs" (LLaMa-2, Mistral 7B as optimizer). — [arXiv 2405.10276](https://arxiv.org/abs/2405.10276) [PP]

### Inferences
- OPRO's own finding is that train-score gaps of 5-20 points are normal and tolerable if the ranking is preserved; AutoPrompter's reported pattern (train 1.0, holdout flat) is a different failure: the prompt contains the answers, which none of these systems measure or block. A held-out reward split (PromptAgent) or a small val subset every k steps (OPRO's `eval_interval`) would detect it; neither is in the current AutoPrompter loop.
- Scoring on a fixed full training set across all iterations (ours) removes the noise-averaging that APE's resampled subsets give, and makes memorization of that exact set reachable.

### Gaps
- No source in this scope reports a train/holdout gap specific to answer-memorization in prompts; the gaps cited are for ordinary instruction overfit.
- PromptWizard's paper reports no train/test gap numbers that I found.

## 4. Cost: LLM calls per run/step

### Takeaway
OPRO is the most expensive per run in scorer calls (hundreds of scored candidates x hundreds of examples), EvoPrompt about 5,000 calls per task under PromptWizard's accounting, PromptAgent a few dozen to ~100 explored prompts, PromptWizard 69 calls. Note the 5,000/18,600/69 figures come from PromptWizard's authors' own comparison (a competitor-authored estimate).

### Cited Findings
- PromptWizard paper cost table (Table 4, BBII): InstructZero/Instinct 1,730 calls (about $0.23); PromptBreeder 18,600 calls (about $2.9); EvoPrompt 5,000 calls = N x T x (1 + D) = 10 x 10 x (1 + 50), about $0.8; PromptWizard 69 calls, 24,978 total tokens, about $0.05. They claim 5x-60x token reduction. The EvoPrompt number is the PromptWizard authors' formula, not EvoPrompt's own report. — [arXiv 2405.18369 s5.2, Table 4](https://arxiv.org/pdf/2405.18369)
- EvoPrompt: population size 6 vs 10 on simple tasks (ASSET) gives similar scores at a 2.5x overhead difference; larger populations help complex tasks (Subj). — [arXiv 2309.08532 App. C.1](https://arxiv.org/pdf/2309.08532)
- PromptAgent exploration cost in number of explored prompts: Greedy-S 34, Greedy-L 72, APE 150 per task; PromptAgent clusters at the top-left (higher accuracy, fewer prompts). The paper says "computation overhead" is analyzed but gives prompt counts, not dollars. — [arXiv 2310.16427 s5.2, Fig. 4a, App. A.3](https://arxiv.org/pdf/2310.16427)
- APE: 150 prompts explored per task in PromptAgent's baseline run (100 initial + resamples, 10 batches x 10); the APE paper includes a cost analysis (App. D) concluding larger models are more cost-efficient for proposal despite higher per-token price. — [arXiv 2310.16427 App. A.3](https://arxiv.org/pdf/2310.16427); [arXiv 2211.01910 s5, App. D](https://arxiv.org/pdf/2211.01910)
- OPRO: default 200 steps x 8 candidates; the paper also notes that good instructions can appear early (e.g. "Let's do the math!" at step 6, train 78.2, versus "Take a deep breath..." at step 107, train 80.2). — [arXiv 2309.03409 s5.2](https://arxiv.org/pdf/2309.03409)
- PromptWizard README: optimization "took around 20 - 30 minutes on average" for GSM8K/SVAMP/AQUARAT/BBII. — [README](https://github.com/microsoft/PromptWizard) [README]

### Inferences
- Per AutoPrompter iteration the cost is one full-dataset run plus one optimizer call; OPRO per step is 8 optimizer samples (one meta-prompt, `n=8` decodes or repeated calls) plus 8 train-subset evaluations; the key cost lever OPRO uses is evaluating on a 3.5%-20% subset, not full data.

### Gaps
- No dollar budget reported by OPRO, APE (in the main body), or PromptAgent.

## 5. Reported gains (benchmarks, models, magnitude)

### Takeaway
Gains are reported as test accuracy versus human prompts and each other; OPRO up to +8% on GSM8K and up to +50% on BBH tasks over "Let's think step by step"/empty; PromptAgent +9 to +11% relative over APE on BBH subsets; EvoPrompt up to +25% on BBH (DE); PromptWizard 90 vs 74.5 on GSM8K (GPT-3.5, vs Instinct). Comparisons across papers are not apples-to-apples (different models, subsets, seeds).

### Cited Findings
- OPRO abstract: "outperform human-designed prompts by up to 8% on GSM8K, and by up to 50% on Big-Bench Hard tasks". — [arXiv 2309.03409 abstract](https://arxiv.org/pdf/2309.03409)
- OPRO Table 4 (GSM8K test, PaLM 2-L scorer): "Let's think step by step" 71.8; Zhou et al. APE prompt 58.8; PaLM 2-L-IT optimizer found "Take a deep breath and work on this problem step-by-step." 80.2. text-bison scorer: Kojima baseline 64.4. — [arXiv 2309.03409 Table 4](https://arxiv.org/pdf/2309.03409)
- OPRO BBH: instructions beat "Let's think step by step" by over 5% on 19/23 tasks (PaLM 2-L scorer) and 15/23 (text-bison); beat the empty-instruction start by over 5% on 20/23 and 15/23. Models: optimizers PaLM 2-L, PaLM 2-L-IT, text-bison, gpt-3.5-turbo, gpt-4; scorers PaLM 2-L, text-bison. — [arXiv 2309.03409 s5.1-5.2, Fig. 5, Table 7](https://arxiv.org/pdf/2309.03409)
- APE: Instruction Induction (24 tasks), InstructGPT zero-shot, interquartile mean 0.810 (APE) vs 0.749 (human); APE equal or better than human on 24/24 after hyperparameter re-tuning, 19/24 in an earlier iteration; BIG-Bench Instruction Induction subset, comparable or better on 17/21 tasks; zero-shot CoT prompt search improved InstructGPT's MultiArith and GSM8K pipeline (Kojima baseline 78.7 / 40.7 quoted). TruthfulQA: over 40% true+informative vs 30% for the human "help" prompt. — [arXiv 2211.01910 s4, App. F](https://arxiv.org/pdf/2211.01910)
- EvoPrompt Table 1 (Alpaca-7b, 7 classification datasets, average): MI 71.07, NI 68.21, APE 73.80, EvoPrompt GA 76.25, DE 77.05. Table 2 (SAMSum ROUGE-1, GPT-3.5): MI 43.95, APE 43.43, GA 45.22, DE 46.49. BBH (22 tasks, GPT-3.5): DE up to +25% and 3.5% average over the "Let's think step by step" 3-shot baseline; GA up to +15%, 2.5% average. Table 12 BBH average: baseline 71.49, APE 71.85, GA 74.18, DE 75.03. — [arXiv 2309.08532 Tables 1, 2, 12, s4.4](https://arxiv.org/pdf/2309.08532)
- PromptAgent Table 1 (BBH 6 tasks, GPT-3.5 base, GPT-4 optimizer, average accuracy): Human ZS 0.513, CoT 0.707, APE 0.690, PromptAgent 0.802. Table 2 (specialized: NCBI/Biosses/MedQA avg) APE 0.582 vs PromptAgent 0.655; (general NLU: Subj/TREC/CB avg) APE 0.778 vs PromptAgent 0.868. Table 3: 12-task average on GPT-3.5 Human 0.552 / APE 0.685 / PromptAgent 0.776; GPT-4 0.759 / 0.762 / 0.839; PaLM 2 0.392 / 0.381 / 0.441. Text claims 28.9%, 9.5%, 11.2% relative improvement over Human ZS, CoT, APE on BBH. — [arXiv 2310.16427 Tables 1-3](https://arxiv.org/pdf/2310.16427)
- PromptWizard Table 2 (zero-shot, GPT-3.5-Turbo): GSM8K InstructZero 74.2, Instinct 74.5, PW 90; AQUARAT 54.3 / 54.7 / 58.2; SVAMP 79.5 / 81 / 82.3. Table 3 BBH (23 tasks): APE 71.85, EvoPrompt 75.03, PW 88.1 (the APE/EvoPrompt numbers are copied from the EvoPrompt paper's Table 12, same values). BBII Table 1: PW best on 13/19 tasks zero-shot and 16/19 one-shot versus 8 and 7 for Instinct. With 5 training examples and with Llama-70B as the optimizer the paper reports a negligible (<1%) drop on its datasets. — [arXiv 2405.18369 Tables 1-3, 5-6, s6](https://arxiv.org/pdf/2405.18369)

### Inferences
- PromptWizard's gains are large partly because it outputs instruction + few-shot examples + CoT + persona, while its comparison baselines are instruction-only; EvoPrompt and OPRO numbers are on different base models; do not compare 90 (PW GSM8K) with 80.2 (OPRO GSM8K, PaLM 2-L).
- None of these gains are measured on LLM-generated synthetic datasets; all use human-labeled benchmarks with official or random test splits.

### Gaps
- PromptWizard v2 numbers vs the Findings-ACL-2025 camera-ready were not compared.
- No standard errors reported for EvoPrompt GPT-3.5 (single seed) or PromptAgent main tables in the text I extracted.

## 6. Code: repos, modules, scorer plug-in, output artifact

### Takeaway
All five repos are small research codebases; scoring is wired to accuracy/metric functions per task, so plugging our own scorer means implementing a per-task class (PromptAgent, PromptWizard, EvoPrompt) or a callable (APE, OPRO).

### Cited Findings
- OPRO: [google-deepmind/opro](https://github.com/google-deepmind/opro); entry `opro/optimization/optimize_instructions.py`, core loop `run_evolution` in `opro/optimization/opt_utils.py`, scorer/optimizer API wrappers in `opro/prompt_utils.py` (`call_openai_server_func`, PaLM), evaluation in `opro/evaluation/eval_utils.py` and `metrics.py`. Scorer plugs in as `call_scorer_server_func(inputs) -> list[str]`; accuracy is computed by task-specific answer parsing in `eval_utils.evaluate_single_instruction`. Output: `save_folder` with `result_by_instruction/*.csv` per instruction and `results.json` containing `meta_prompts`, `old_instructions_and_scores`, `old_instructions_and_scores_raw`. Last commit seen 2024-12-04. — [CODE]
- APE: [keirp/automatic_prompt_engineer](https://github.com/keirp/automatic_prompt_engineer); `automatic_prompt_engineer/ape.py` (`find_prompts`, `simple_ape`), `generate.py`, `evaluate.py`, `evaluation/bandits.py` (UCB), `evaluation/likelihood.py`. Custom scorer: `evaluation.method` can be any callable `(prompts, eval_template, eval_data, demos_template, few_shot_data, config) -> EvaluationResult` (used by `experiments/evaluation/instruction_induction/exec_accuracy.py`). Output: an `EvaluationResult` with `.sorted()`, experiment script writes a text file with best prompt and test score. Last commit 2023-05-25 (unmaintained since). — [CODE]
- EvoPrompt: [beeevita/EvoPrompt](https://github.com/beeevita/EvoPrompt); `evoluter.py` (`Evoluter`, `GAEvoluter`, `DEEvoluter`/`ParaEvoluter`), `evaluator.py` (`CLSEvaluator`, `SumEvaluator`, `SimEvaluator`, each with `forward(prompt, eval_src, eval_tgt) -> {hypos, scores}`), `llm_client.py`, `data/template_ga.py`, `data/template_de.py`, `BBH/` subfolder with its own copy. Scorer plugs in by subclassing `Evaluator`. Output: per-step population files with scores via `write_step`, a JSON cache of evaluated prompts per seed. Last commit 2025-09-22. — [CODE]
- PromptAgent: [XinyuanWangCS/PromptAgent](https://github.com/XinyuanWangCS/PromptAgent); `src/main.py`, `src/prompt_optim_agent/agent.py`, `search_algo/mcts.py`, `search_algo/beam_search.py`, `world_model/gradient_descent.py`, `world_model/prompts/gradient_descent_prompts.py`, `tasks/base_task.py` (subclass `BaseTask`, override `cal_correct`/`cal_metric`/`clean_response`), YAML config. Output: log directory per experiment with `data.json` (all paths and nodes with reward, Q, UCT, test_metric) and logs. Last commit 2025-07-17. — [CODE]
- PromptWizard: [microsoft/PromptWizard](https://github.com/microsoft/PromptWizard); `promptwizard/glue/promptopt/instantiate.py` (`GluePromptOpt.get_best_prompt`, `.evaluate`), `techniques/critique_n_refine/core_logic.py`, `prompt_pool.yaml`; user supplies a `DatasetSpecificProcessing` subclass (pickled) with answer extraction/comparison, train/test `.jsonl` with `question`/`answer`, YAML configs. Output: `get_best_prompt()` returns (best prompt, expert profile); synthetic examples written to `train_synthetic.jsonl`. Last commit 2025-08-04. — [CODE], [README](https://github.com/microsoft/PromptWizard) [README]

### Inferences
- Of the five, OPRO's `run_evolution` and PromptAgent's `world_model/gradient_descent.py` are the two cleanest pieces to port: OPRO for the meta-prompt builder (`gen_meta_prompt`), PromptAgent for the error-example formatting and train/eval split logic.

### Gaps
- Did not run any of the code; no verification that the repos reproduce paper numbers.
- OPRO repo uses the pre-1.0 `openai` (0.27.2) and `google.generativeai` 0.1.0 per its README, so porting needs adapting API calls. — [README](https://github.com/google-deepmind/opro) [README]

## 7. Is our design closest to OPRO? What does OPRO do that we don't?

### Takeaway
Yes, structurally closest to OPRO (single trajectory, history of prompts+scores in the meta-prompt, duplicate rejection), with PromptAgent-style error feedback bolted on. OPRO differs on 8 points that all plausibly matter for overfitting and stability, listed below.

### Cited Findings (OPRO behaviors that AutoPrompter, as described, lacks)
- Multiple candidates per step: 8 sampled from the same meta-prompt; 1/2/4/8/16 ablation shows 8 best. — [arXiv 2309.03409 s2.3, s5.3](https://arxiv.org/pdf/2309.03409)
- History sorted by score ascending, truncated to the top 20 by score (not by recency); scores bucketed to integers 0-100 in the prompt; low-score instructions thresholded out. — [arXiv 2309.03409 s4.2](https://arxiv.org/pdf/2309.03409); [opt_utils.py](https://github.com/google-deepmind/opro/blob/main/opro/optimization/opt_utils.py) [CODE]
- Task exemplars (3 random training Q/A pairs, with `<INS>` placeholder showing where the instruction goes) in every meta-prompt, resampled each step. — [arXiv 2309.03409 Fig. 3, s4.2](https://arxiv.org/pdf/2309.03409)
- Scoring on a small random subset of the data (3.5% GSM8K, 20% BBH), not the full set; optional validation on a disjoint subset every 3 steps. — [arXiv 2309.03409 s4.1](https://arxiv.org/pdf/2309.03409); [optimize_instructions.py](https://github.com/google-deepmind/opro/blob/main/opro/optimization/optimize_instructions.py) [CODE]
- Length cap (500 chars) and "no digits in the instruction" filter for GSM8K, which blocks inserting numeric answers into the prompt. — [optimize_instructions.py / opt_utils.py](https://github.com/google-deepmind/opro/blob/main/opro/optimization/opt_utils.py) [CODE]
- Optimizer temperature 1.0 for diversity versus scorer temperature 0. — [arXiv 2309.03409 s5.1](https://arxiv.org/pdf/2309.03409)
- Where OPRO does not do something we do: failure feedback (OPRO's paper says error exemplars gave similar results and calls richer feedback future work), and an explicit stagnation-triggered "diverse" strategy (OPRO relies on temperature and multi-sampling; APE's UCB bandit and EvoPrompt's population provide diversity structurally). — [arXiv 2309.03409 Limitations](https://arxiv.org/pdf/2309.03409)
- What the closest "feedback + search" systems add: PromptAgent keeps a separate held-out reward set (default 150) and explores several branches, so one overfit prompt does not end the search. — [arXiv 2310.16427 App. A.2](https://arxiv.org/pdf/2310.16427)

### Inferences
- The `<INS>`-style no-digit rule and the 500-char cap are the closest thing in these codebases to blocking answer memorization; neither is principled (they are GSM8K-specific), so a leakage check (e.g. reject prompts that contain n-grams or numbers from training answers) would be our own addition.
- Highest-value OPRO ports, in rough order of expected effect on the overfit problem: (1) score on a random subset and keep a disjoint validation subset, select the final prompt by validation score; (2) sample several candidates per step and drop duplicates through the existing ledger; (3) show the optimizer the top-k sorted by score instead of compressed recent history; (4) put 3 random exemplars in the meta-prompt rather than failing items verbatim. These are inferences from the cited design differences, not tested.
- OPRO's reported behavior suggests train-over-test gaps of 5-20 points even with these controls, so a holdout of 1.0 -> flat gap would remain a signal worth tracking, not eliminating.

### Gaps
- I do not have AutoPrompter's source in this research scope beyond the user's description; claims about what it "lacks" rely on that description.
