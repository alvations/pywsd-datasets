"""Report OEWN/OMW sense-ID resolution rate per dataset config.

Reads each ``data/<config>/*.parquet`` and measures the fraction of
instances whose ``sense_ids_wordnet`` list is non-empty — i.e. how
many source sense keys we successfully mapped to the modern lexicon.

Usage::

    python -m pywsd_datasets.scripts.coverage_report
    python -m pywsd_datasets.scripts.coverage_report --data build/
"""

from __future__ import annotations

import argparse
from pathlib import Path


def analyze(data_root: Path) -> list[tuple[str, int, int, float]]:
    import pyarrow.parquet as pq

    rows: list[tuple[str, int, int, float]] = []
    for config_dir in sorted(p for p in data_root.iterdir() if p.is_dir()):
        for parquet in sorted(config_dir.glob("*.parquet")):
            t = pq.read_table(parquet, columns=["sense_ids_wordnet"])
            total = t.num_rows
            resolved = sum(
                1 for ids in t.column("sense_ids_wordnet").to_pylist() if ids
            )
            pct = 100.0 * resolved / total if total else 0.0
            rows.append((f"{config_dir.name}/{parquet.stem}",
                         resolved, total, pct))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path,
                    default=Path(__file__).resolve().parents[3] / "data")
    args = ap.parse_args(argv)

    root: Path = args.data
    if not root.exists():
        print(f"no data dir at {root}; run build_all first.", flush=True)
        return 1

    rows = analyze(root)
    if not rows:
        print(f"no parquet files under {root}", flush=True)
        return 1

    width = max(len(name) for name, *_ in rows)
    print(f"{'config/split':<{width}}  resolved /  total     %")
    print("-" * (width + 30))
    for name, resolved, total, pct in rows:
        print(f"{name:<{width}}  {resolved:>8} / {total:>6}  {pct:6.2f}")

    # Summary
    tot_r = sum(r for _, r, _, _ in rows)
    tot_t = sum(t for _, _, t, _ in rows)
    if tot_t:
        print("-" * (width + 30))
        print(f"{'TOTAL':<{width}}  {tot_r:>8} / {tot_t:>6}  "
              f"{100.0*tot_r/tot_t:6.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
