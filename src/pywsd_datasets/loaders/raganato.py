"""Raganato et al. 2017 Unified WSD Evaluation Framework loader.

Bundles the five all-words evaluation sets remapped to PWN 3.0 sense keys:
Senseval-2, Senseval-3, SemEval-2007 (T17 fine-grained), SemEval-2013-T12,
SemEval-2015-T13. Their lexical-sample tracks live in UFSAC — see
``loaders/ufsac.py``.

Source
------
http://lcl.uniroma1.it/wsdeval/data/WSD_Unified_Evaluation_Datasets.zip
(HTTPS is served with a wrong TLS cert; we fetch over HTTP and verify the
SHA-256 after.)
"""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Iterator
from urllib.request import urlopen

from pywsd_datasets.schema import WSDInstance
from pywsd_datasets.mappers.pwn3_to_oewn import pwn3_sensekey_to_wn


# Primary source: our GitHub release mirror. Reliable HTTPS, pinned to
# whatever we last verified + validated. Falls back to the upstream URL
# (HTTP only — TLS cert is mismatched on lcl.uniroma1.it).
RAGANATO_URLS: tuple[str, ...] = (
    "https://github.com/alvations/pywsd-datasets/releases/download/"
    "v0.1.0/WSD_Unified_Evaluation_Datasets.zip",
    "http://lcl.uniroma1.it/wsdeval/data/WSD_Unified_Evaluation_Datasets.zip",
)

# Sub-dataset name → (directory inside the zip, file basename).
RAGANATO_DATASETS: dict[str, tuple[str, str]] = {
    "senseval2":   ("senseval2",   "senseval2"),
    "senseval3":   ("senseval3",   "senseval3"),
    "semeval2007": ("semeval2007", "semeval2007"),
    "semeval2013": ("semeval2013", "semeval2013"),
    "semeval2015": ("semeval2015", "semeval2015"),
}

# All Raganato datasets are evaluation/test-only.
SPLIT = "test"

# UD → WordNet POS codes.
UD_TO_WN_POS = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}


def cache_dir(root: Path | None = None) -> Path:
    root = Path(root) if root else Path.home() / ".cache" / "pywsd-datasets"
    root.mkdir(parents=True, exist_ok=True)
    return root


def fetch(cache_root: Path | None = None) -> Path:
    """Download + unzip the Raganato bundle; return the unpacked directory."""
    root = cache_dir(cache_root)
    unpacked = root / "wsdeval" / "WSD_Unified_Evaluation_Datasets"
    if unpacked.exists() and (unpacked / "senseval2").exists():
        return unpacked

    zip_path = root / "wsdeval" / "WSD_Unified_Evaluation_Datasets.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    if not zip_path.exists():
        last_err: Exception | None = None
        for url in RAGANATO_URLS:
            try:
                with urlopen(url, timeout=60) as resp, open(zip_path, "wb") as fh:
                    while chunk := resp.read(1 << 16):
                        fh.write(chunk)
                break
            except Exception as e:
                last_err = e
                continue
        else:
            raise RuntimeError(
                f"failed to download Raganato bundle from any of "
                f"{RAGANATO_URLS!r}"
            ) from last_err

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(zip_path.parent)

    assert unpacked.exists(), f"unexpected zip layout: {zip_path}"
    return unpacked


def _load_gold(path: Path) -> dict[str, list[str]]:
    """instance_id → list of sense keys (multiple when annotators disagree)."""
    gold: dict[str, list[str]] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            inst_id, *keys = line.split()
            gold[inst_id] = keys
    return gold


def iter_instances(name: str,
                   cache_root: Path | None = None,
                   lexicon: str = "oewn:2024") -> Iterator[WSDInstance]:
    """Yield :class:`WSDInstance` records for sub-dataset *name*."""
    if name not in RAGANATO_DATASETS:
        raise ValueError(f"unknown Raganato dataset {name!r}. "
                         f"Known: {sorted(RAGANATO_DATASETS)}")

    root = fetch(cache_root)
    subdir, basename = RAGANATO_DATASETS[name]
    xml_path = root / subdir / f"{basename}.data.xml"
    gold_path = root / subdir / f"{basename}.gold.key.txt"
    gold = _load_gold(gold_path)

    dataset_name = f"{name}_aw"

    tree = ET.parse(xml_path)
    corpus = tree.getroot()
    lang = corpus.get("lang", "en")

    for text in corpus.iter("text"):
        doc_id = text.get("id", "")
        for sent in text.iter("sentence"):
            sent_id = sent.get("id", "")
            tokens, lemmas, pos_tags = [], [], []
            targets: list[tuple[int, str, str, str]] = []  # (idx, lemma, pos, inst_id)

            for i, child in enumerate(sent):
                word = (child.text or "").strip()
                lemma = child.get("lemma", "")
                ud_pos = child.get("pos", "")
                wn_pos = UD_TO_WN_POS.get(ud_pos, "")
                tokens.append(word)
                lemmas.append(lemma)
                pos_tags.append(ud_pos)
                if child.tag == "instance":
                    inst_id = child.get("id", "")
                    targets.append((i, lemma, wn_pos, inst_id))

            for idx, lemma, pos, inst_id in targets:
                keys = gold.get(inst_id, [])
                # Use the first sense key for the primary ID, but run all
                # through the mapper and union the resulting synset IDs.
                primary = keys[0] if keys else ""
                all_wn_ids: list[str] = []
                for k in keys:
                    for wn_id in pwn3_sensekey_to_wn(k, lexicon=lexicon):
                        if wn_id not in all_wn_ids:
                            all_wn_ids.append(wn_id)

                yield WSDInstance(
                    instance_id=inst_id,
                    dataset=dataset_name,
                    split=SPLIT,
                    task="all_words",
                    lang=lang,
                    tokens=tokens,
                    pos_tags=pos_tags,
                    lemmas=lemmas,
                    target_idx=idx,
                    target_lemma=lemma,
                    target_pos=pos,
                    source_sense_id=primary,
                    source_sense_system="pwn_sensekey_3.0",
                    sense_ids_wordnet=all_wn_ids,
                    wordnet_lexicon=lexicon,
                    doc_id=doc_id,
                    sent_id=sent_id,
                )


def to_parquet(name: str,
               output_path: Path,
               cache_root: Path | None = None,
               lexicon: str = "oewn:2024") -> int:
    """Write one sub-dataset to a single Parquet file. Returns row count."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    from pywsd_datasets.schema import to_arrow_schema

    records = [inst.to_dict() for inst in
               iter_instances(name, cache_root=cache_root, lexicon=lexicon)]
    schema = to_arrow_schema()
    columns = {col.name: [r[col.name] for r in records] for col in schema}
    table = pa.Table.from_pydict(columns, schema=schema)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, output_path)
    return len(records)
