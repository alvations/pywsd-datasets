"""Build every dataset config into ``data/<config>/<split>.parquet``.

Usage::

    # English Raganato bundle (always runs, ~1 MB fetch):
    python -m pywsd_datasets.scripts.build_all

    # With UFSAC corpora (SemCor / WNGT / MASC / lex-sample). Needs the
    # UFSAC 2.1 tarball unpacked locally:
    python -m pywsd_datasets.scripts.build_all \\
        --ufsac-root ~/.cache/pywsd-datasets/ufsac/ufsac-public-2.1

    # Subset:
    python -m pywsd_datasets.scripts.build_all \\
        --ufsac-root PATH --ufsac semcor masc
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pywsd_datasets.loaders.raganato import (
    RAGANATO_DATASETS, to_parquet as raganato_to_parquet,
)
from pywsd_datasets.loaders.ufsac import (
    UFSAC_CORPORA, to_parquet as ufsac_to_parquet,
)


def build_raganato(names: list[str], out_dir: Path, lexicon: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in names:
        if name not in RAGANATO_DATASETS:
            print(f"  skip unknown raganato: {name}")
            continue
        config = f"en-{name}-aw"
        parquet = out_dir / config / "test.parquet"
        n = raganato_to_parquet(name, parquet, lexicon=lexicon)
        counts[config] = n
        print(f"  {config:40s} {n:>8} rows -> {parquet}")
    return counts


def build_ufsac(names: list[str], ufsac_root: Path,
                out_dir: Path, lexicon: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in names:
        if name not in UFSAC_CORPORA:
            print(f"  skip unknown ufsac: {name}")
            continue
        meta = UFSAC_CORPORA[name]
        config = f"en-{meta['dataset']}"
        parquet = out_dir / config / f"{meta['split']}.parquet"
        n = ufsac_to_parquet(name, parquet, ufsac_root, lexicon=lexicon)
        counts[f"{config}/{meta['split']}"] = n
        print(f"  {config:40s} [{meta['split']:>5}] {n:>8} rows -> {parquet}")
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parents[3] / "data")
    ap.add_argument("--raganato", nargs="*", default=list(RAGANATO_DATASETS),
                    help="Raganato sub-datasets (default: all)")
    ap.add_argument("--ufsac", nargs="*", default=None,
                    help="UFSAC corpora to build (requires --ufsac-root)")
    ap.add_argument("--ufsac-root", type=Path, default=None,
                    help="Path to unpacked ufsac-public-2.1 dir")
    ap.add_argument("--lexicon", default="oewn:2024")
    args = ap.parse_args(argv)

    print(f"building to {args.out} (lexicon={args.lexicon})")
    if args.raganato:
        print("[raganato]")
        build_raganato(args.raganato, args.out, args.lexicon)

    if args.ufsac is not None:
        if args.ufsac_root is None:
            raise SystemExit("--ufsac requires --ufsac-root")
        names = args.ufsac or list(UFSAC_CORPORA)
        print("[ufsac]")
        build_ufsac(names, args.ufsac_root, args.out, args.lexicon)
    elif args.ufsac_root is not None:
        print("[ufsac]")
        build_ufsac(list(UFSAC_CORPORA), args.ufsac_root, args.out, args.lexicon)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
