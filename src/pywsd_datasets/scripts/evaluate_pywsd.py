"""Evaluate pywsd methods against the unified test sets.

For each test instance, run each WSD method and compare the returned
synset's modern-wn id against the gold ``sense_ids_wordnet`` list.

Usage::

    python -m pywsd_datasets.scripts.evaluate_pywsd            # all eval configs
    python -m pywsd_datasets.scripts.evaluate_pywsd \\
        --configs en-senseval2-aw en-senseval3-aw              # subset
    python -m pywsd_datasets.scripts.evaluate_pywsd \\
        --methods simple_lesk first_sense                      # subset of methods
    python -m pywsd_datasets.scripts.evaluate_pywsd \\
        --limit 200                                            # smoke run

Accuracy is computed only over instances with non-empty
``sense_ids_wordnet``; instances that failed to resolve during dataset
build are excluded from both numerator and denominator (and reported).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


# These are the test-only configs. Training configs (semcor / wngt / masc)
# don't have held-out labels in our layout, so aren't evaluated here.
TEST_CONFIGS: dict[str, str] = {
    "en-senseval2-aw": "test",
    "en-senseval3-aw": "test",
    "en-semeval2007-aw": "test",
    "en-semeval2013-aw": "test",
    "en-semeval2015-aw": "test",
    "en-senseval2_ls": "test",
    "en-senseval3_ls": "test",
    "en-semeval2007_t17_ls": "test",
}


def load_rows(parquet_path: Path) -> list[dict]:
    import pyarrow.parquet as pq
    return pq.read_table(parquet_path).to_pylist()


def detokenize(tokens: list[str]) -> str:
    """UFSAC/Raganato tokens with underscores for MWEs; dot/comma spacing."""
    return " ".join(tokens).replace("_", " ")


def _wn_pos(pos: str) -> str | None:
    return pos if pos in ("n", "v", "a", "r") else None


def run_method(method: str, sentence: str, lemma: str, pos: str | None):
    """Dispatch to the right pywsd call. Returns a Synset or None."""
    from pywsd.lesk import simple_lesk, adapted_lesk, cosine_lesk, original_lesk
    from pywsd.similarity import max_similarity
    from pywsd.baseline import first_sense, random_sense, max_lemma_count

    if method == "simple_lesk":
        return simple_lesk(sentence, lemma, pos=pos)
    if method == "adapted_lesk":
        return adapted_lesk(sentence, lemma, pos=pos)
    if method == "cosine_lesk":
        return cosine_lesk(sentence, lemma, pos=pos)
    if method == "original_lesk":
        return original_lesk(sentence, lemma)
    if method.startswith("max_similarity_"):
        opt = method.removeprefix("max_similarity_")
        return max_similarity(sentence, lemma, option=opt, pos=pos)
    if method == "first_sense":
        try:
            return first_sense(lemma, pos=pos)
        except Exception:
            return None
    if method == "random_sense":
        try:
            return random_sense(lemma, pos=pos)
        except Exception:
            return None
    if method == "max_lemma_count":
        return max_lemma_count(lemma)
    raise ValueError(f"unknown method {method!r}")


DEFAULT_METHODS: list[str] = [
    "first_sense",
    "random_sense",
    "max_lemma_count",
    "simple_lesk",
    "adapted_lesk",
    "cosine_lesk",
    "max_similarity_path",
    "max_similarity_wup",
    "max_similarity_lch",
    "max_similarity_res",
    "max_similarity_jcn",
    "max_similarity_lin",
]


def evaluate_one(rows: list[dict], method: str, limit: int | None = None) -> dict:
    total = 0                # instances with non-empty gold
    correct = 0
    skipped_nogold = 0
    errors = 0
    t0 = time.time()
    n = len(rows) if limit is None else min(limit, len(rows))
    for i in range(n):
        row = rows[i]
        gold = row.get("sense_ids_wordnet") or []
        if not gold:
            skipped_nogold += 1
            continue
        sentence = detokenize(row["tokens"])
        lemma = row["target_lemma"]
        pos = _wn_pos(row["target_pos"])
        try:
            pred = run_method(method, sentence, lemma, pos)
        except Exception:
            errors += 1
            continue
        if pred is None:
            errors += 1
            continue
        pid = getattr(pred, "id", None)
        # Methods that return ranked lists (unused in default loop)
        if pid is None:
            errors += 1
            continue
        total += 1
        if pid in gold:
            correct += 1
    elapsed = time.time() - t0
    acc = correct / total if total else 0.0
    return {
        "method": method,
        "total": total,
        "correct": correct,
        "accuracy": acc,
        "skipped_nogold": skipped_nogold,
        "errors": errors,
        "elapsed_sec": elapsed,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path,
                    default=Path(__file__).resolve().parents[3] / "data")
    ap.add_argument("--configs", nargs="*", default=list(TEST_CONFIGS))
    ap.add_argument("--methods", nargs="*", default=DEFAULT_METHODS)
    ap.add_argument("--limit", type=int, default=None,
                    help="max rows per config (for quick runs)")
    ap.add_argument("--out", type=Path, default=None,
                    help="optional JSONL results dump")
    args = ap.parse_args(argv)

    # One-time import + lexicon warmup
    from pywsd._wordnet import _get
    _get()

    results = []
    for config in args.configs:
        split = TEST_CONFIGS.get(config)
        if split is None:
            print(f"skip non-test config: {config}", file=sys.stderr)
            continue
        parquet = args.data / config / f"{split}.parquet"
        if not parquet.exists():
            print(f"missing {parquet}; run build_all first", file=sys.stderr)
            continue
        rows = load_rows(parquet)

        print(f"\n## {config}/{split}   ({len(rows)} rows)")
        print(f"{'method':<22} {'acc':>7} {'n':>6} {'err':>5} {'nogold':>7} {'sec':>7}")
        for method in args.methods:
            r = evaluate_one(rows, method, limit=args.limit)
            r.update({"config": config, "split": split})
            results.append(r)
            print(f"{method:<22} {r['accuracy']*100:>6.2f}% {r['total']:>6} "
                  f"{r['errors']:>5} {r['skipped_nogold']:>7} "
                  f"{r['elapsed_sec']:>6.1f}s", flush=True)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as fh:
            for r in results:
                fh.write(json.dumps(r) + "\n")
        print(f"\nwrote {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
