#!/usr/bin/env python3
"""
Split one dataset JSON into train, val and test files for experiment.acceptance: val.

The input is a list of {"input": ..., "expected_output": ...} objects (the format of
storage.dataset_file). Entries with the same input are dropped after the first, so no
question appears in two sets. The split is random but repeatable for a given seed.

Usage:
    python3 scripts/split_dataset.py grounded.json --out-dir data/ --val 30 --test 30
    python3 scripts/split_dataset.py grounded.json --out-dir data/ --val 0.3 --test 0.3 --seed 1

--val and --test take a count (integer) or a fraction of the deduplicated entries
(number below 1). Whatever is left is train. The files are written as
<out-dir>/train.json, val.json and test.json.
"""

import argparse
import json
import os
import random
import sys


def split_size(value: float, total: int) -> int:
    return int(round(value * total)) if value < 1 else int(value)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", help="input JSON list of {input, expected_output}")
    parser.add_argument("--out-dir", required=True, help="directory for train.json, val.json, test.json")
    parser.add_argument("--val", type=float, required=True, help="val size: count, or fraction if < 1")
    parser.add_argument("--test", type=float, required=True, help="test size: count, or fraction if < 1")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    with open(args.dataset) as f:
        entries = json.load(f)
    unique = list({e["input"]: e for e in reversed(entries)}.values())[::-1]  # first occurrence wins
    dropped = len(entries) - len(unique)

    n_val, n_test = split_size(args.val, len(unique)), split_size(args.test, len(unique))
    if n_val + n_test >= len(unique):
        print(f"error: val ({n_val}) + test ({n_test}) leave no train entries out of {len(unique)}",
              file=sys.stderr)
        return 1

    random.Random(args.seed).shuffle(unique)
    splits = {"val": unique[:n_val], "test": unique[n_val:n_val + n_test], "train": unique[n_val + n_test:]}

    os.makedirs(args.out_dir, exist_ok=True)
    for name, items in splits.items():
        with open(os.path.join(args.out_dir, f"{name}.json"), "w") as f:
            json.dump(items, f, indent=2)
    print(f"train {len(splits['train'])}, val {n_val}, test {n_test} written to {args.out_dir}"
          + (f" ({dropped} duplicate inputs dropped)" if dropped else ""))
    for name in ("val", "test"):
        if len(splits[name]) < 30:
            print(f"warning: {name} has {len(splits[name])} items; 30+ is recommended", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
