"""Build every known dataset config into ``data/<config>/test.parquet``.

Usage::

    python -m pywsd_datasets.scripts.build_all
    python -m pywsd_datasets.scripts.build_all --out build/
    python -m pywsd_datasets.scripts.build_all --datasets senseval2 senseval3
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pywsd_datasets.loaders.raganato import RAGANATO_DATASETS, to_parquet


def build(datasets: list[str], out_dir: Path, lexicon: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in datasets:
        if name not in RAGANATO_DATASETS:
            print(f"  skip unknown: {name}")
            continue
        config = f"en-{name}-aw"
        parquet = out_dir / config / "test.parquet"
        n = to_parquet(name, parquet, lexicon=lexicon)
        counts[config] = n
        print(f"  {config:32s} {n:>6} rows -> {parquet}")
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parents[3] / "data")
    ap.add_argument("--datasets", nargs="+", default=list(RAGANATO_DATASETS))
    ap.add_argument("--lexicon", default="oewn:2024")
    args = ap.parse_args(argv)

    print(f"building to {args.out} (lexicon={args.lexicon})")
    build(args.datasets, args.out, args.lexicon)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
