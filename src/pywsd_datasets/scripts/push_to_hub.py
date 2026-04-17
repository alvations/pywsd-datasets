"""Upload built parquet dataset to the Hugging Face Hub.

Usage::

    huggingface-cli login                       # one-time
    python -m pywsd_datasets.scripts.push_to_hub \\
        --repo alvations/pywsd-datasets \\
        --data data/

Relies on the no-code HF dataset format: directory structure
``data/<config>/<split>.parquet`` is recognised by the ``datasets``
library via the repo's ``README.md`` YAML frontmatter.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="HF repo id, e.g. alvations/pywsd-datasets")
    ap.add_argument("--data", type=Path,
                    default=Path(__file__).resolve().parents[3] / "data")
    ap.add_argument("--message", default="Update parquet data")
    ap.add_argument("--private", action="store_true")
    args = ap.parse_args(argv)

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError as e:
        raise SystemExit(
            "pip install huggingface-hub  (or `pip install pywsd-datasets[hf]`)"
        ) from e

    api = HfApi()
    create_repo(args.repo, repo_type="dataset", exist_ok=True, private=args.private)
    api.upload_folder(
        folder_path=str(args.data),
        path_in_repo="data",
        repo_id=args.repo,
        repo_type="dataset",
        commit_message=args.message,
    )
    # Also push the dataset card.
    readme = args.data.parent / "README.md"
    if readme.exists():
        api.upload_file(
            path_or_fileobj=str(readme),
            path_in_repo="README.md",
            repo_id=args.repo,
            repo_type="dataset",
            commit_message=args.message,
        )
    print(f"pushed {args.data} -> https://huggingface.co/datasets/{args.repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
