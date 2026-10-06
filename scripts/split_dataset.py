"""Split a grounded Q&A dataset (list of {input, expected_output, metadata}) into train/val/test.

Stratifies by metadata.source so each split keeps the same source mix as the
input, and splits deterministically (seeded shuffle) so re-runs are stable.

Usage: python3 split_dataset.py IN_FILE OUT_DIR [TRAIN_RATIO VAL_RATIO TEST_RATIO] [SEED]
Writes OUT_DIR/train.json, OUT_DIR/val.json, OUT_DIR/test.json.
"""
import json
import os
import random
import sys
from collections import Counter, defaultdict

in_file = sys.argv[1]
out_dir = sys.argv[2]
ratios = tuple(float(x) for x in sys.argv[3:6]) if len(sys.argv) > 5 else (0.34, 0.33, 0.33)
seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
assert abs(sum(ratios) - 1.0) < 1e-6, "ratios must sum to 1"

items = json.load(open(in_file))
by_source = defaultdict(list)
for it in items:
    by_source[it.get("metadata", {}).get("source", "")].append(it)

rng = random.Random(seed)
splits = {"train": [], "val": [], "test": []}
names = list(splits)
for source, group in by_source.items():
    group = group[:]
    rng.shuffle(group)
    n = len(group)
    n_train = round(n * ratios[0])
    n_val = round(n * ratios[1])
    cuts = {"train": group[:n_train], "val": group[n_train:n_train + n_val], "test": group[n_train + n_val:]}
    for name in names:
        splits[name] += cuts[name]

os.makedirs(out_dir, exist_ok=True)
for name in names:
    rng.shuffle(splits[name])
    json.dump(splits[name], open(os.path.join(out_dir, f"{name}.json"), "w"), indent=2)

print(f"{in_file}: {len(items)} items -> " + ", ".join(f"{n}={len(splits[n])}" for n in names))
for name in names:
    print(f"  {name} sources:", dict(Counter(it["metadata"]["source"] for it in splits[name])))
