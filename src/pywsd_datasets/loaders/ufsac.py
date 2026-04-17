"""UFSAC v2.1 loader — SemCor, WNGT, MASC, OMSTI, Senseval lex-sample.

Unification Framework for Sense Annotated Corpora (Vial, Lecouteux,
Schwab 2018). MIT-licensed; unifies 15+ sense-tagged English corpora
with every sense key remapped to PWN 3.0.

Upstream: https://github.com/getalp/UFSAC → a single ~2 GB Google Drive
tarball (last updated Oct 2018). Because Drive links are flaky and
bandwidth-metered, the loader takes an already-extracted ``ufsac_root``
path; mirror responsibility is out of scope here. Future revs may ship
per-corpus Parquet files via the ``alvations/pywsd-datasets`` HF dataset.

UFSAC XML schema (one file per corpus)::

    <corpus>
      <document id="...">
        <paragraph>
          <sentence>
            <word surface_form="The" pos="DT" />
            <word surface_form="cat" lemma="cat" pos="NN" wn30_key="cat%1:05:00::" />
            ...
          </sentence>
        </paragraph>
      </document>
    </corpus>

* ``pos`` uses Penn Treebank tags (``NN``, ``VBD``, ``JJ``, ``RB`` …), not UD.
* Only ``<word>`` elements carrying a ``wn30_key`` attribute become
  sense-annotated target instances; the rest become plain context tokens.
* Multi-word expressions are single words with underscores, e.g.
  ``surface_form="Fulton_County_Grand_Jury"``.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from pywsd_datasets.schema import WSDInstance
from pywsd_datasets.mappers.pwn3_to_oewn import pwn3_sensekey_to_wn


# Human-facing corpus name → (xml filename inside UFSAC root, dataset tag,
# task type, split). Only includes corpora that carry their own signal —
# the UFSAC ``raganato_*`` files duplicate the bundle our raganato loader
# already ships, and the auto-tagged OMSTI / Train-O-Matic sets are out
# of scope for v0.2.
UFSAC_CORPORA: dict[str, dict[str, str]] = {
    "semcor": {
        "xml": "semcor.xml",
        "dataset": "semcor",
        "task": "all_words",
        "split": "train",
    },
    "wngt": {
        "xml": "wngt.xml",
        "dataset": "wngt",
        "task": "all_words",
        "split": "train",
    },
    "masc": {
        "xml": "masc.xml",
        "dataset": "masc",
        "task": "all_words",
        "split": "train",
    },
    "senseval2_ls_train": {
        "xml": "senseval2_lexical_sample_train.xml",
        "dataset": "senseval2_ls",
        "task": "lexical_sample",
        "split": "train",
    },
    "senseval2_ls_test": {
        "xml": "senseval2_lexical_sample_test.xml",
        "dataset": "senseval2_ls",
        "task": "lexical_sample",
        "split": "test",
    },
    "senseval3_ls_train": {
        "xml": "senseval3task6_train.xml",
        "dataset": "senseval3_ls",
        "task": "lexical_sample",
        "split": "train",
    },
    "senseval3_ls_test": {
        "xml": "senseval3task6_test.xml",
        "dataset": "senseval3_ls",
        "task": "lexical_sample",
        "split": "test",
    },
    "semeval2007_t17": {
        "xml": "semeval2007task17.xml",
        "dataset": "semeval2007_t17_ls",
        "task": "lexical_sample",
        "split": "test",
    },
}


def _penn_to_wn_pos(penn: str) -> str:
    """Penn Treebank POS → single-letter WordNet POS ('' if unknown)."""
    if not penn:
        return ""
    p2 = penn[:2].upper()
    if p2 == "NN":
        return "n"
    if p2 == "VB":
        return "v"
    if p2 == "JJ":
        return "a"
    if p2 == "RB":
        return "r"
    return ""


def iter_instances(corpus: str,
                   ufsac_root: Path,
                   lexicon: str = "oewn:2024",
                   limit: int | None = None) -> Iterator[WSDInstance]:
    """Yield :class:`WSDInstance` rows from a single UFSAC corpus XML.

    *ufsac_root* must be the directory containing the UFSAC XML files
    (the unpacked ``ufsac-public-2.1`` tarball).

    Large corpora (``omsti``, ``wngt``) stream via ``iterparse`` so the
    whole XML never needs to live in memory.
    """
    if corpus not in UFSAC_CORPORA:
        raise ValueError(f"unknown UFSAC corpus {corpus!r}. "
                         f"Known: {sorted(UFSAC_CORPORA)}")

    meta = UFSAC_CORPORA[corpus]
    xml_path = Path(ufsac_root) / meta["xml"]
    if not xml_path.exists():
        raise FileNotFoundError(
            f"missing UFSAC file {xml_path}. Unpack UFSAC 2.1 into "
            f"{ufsac_root}."
        )

    dataset = meta["dataset"]
    task = meta["task"]
    split = meta["split"]

    doc_id = ""
    sent_idx = 0
    emitted = 0

    # iterparse — capture <document> start tags for doc_id, emit one row
    # per sense-annotated <word> when a </sentence> closes.
    context: ET.iterparse = ET.iterparse(
        xml_path, events=("start", "end")
    )

    tokens: list[str] = []
    pos_tags: list[str] = []
    lemmas: list[str] = []
    # targets collect (token_idx, lemma, wn_pos, keys) per sentence
    targets: list[tuple[int, str, str, list[str]]] = []

    for event, elem in context:
        tag = elem.tag
        if event == "start":
            if tag == "document":
                doc_id = elem.get("id") or elem.get("name") or doc_id
            elif tag == "sentence":
                tokens.clear()
                pos_tags.clear()
                lemmas.clear()
                targets.clear()
            continue

        # event == "end"
        if tag == "word":
            surface = elem.get("surface_form", "")
            lemma = elem.get("lemma", "")
            penn_pos = elem.get("pos", "")
            wn_pos = _penn_to_wn_pos(penn_pos)
            wn30_key = elem.get("wn30_key", "")

            idx = len(tokens)
            tokens.append(surface)
            pos_tags.append(penn_pos)
            lemmas.append(lemma)

            if wn30_key:
                # UFSAC space-separates multiple keys when the gold
                # annotation is itself multi-valued.
                keys = wn30_key.split()
                targets.append((idx, lemma, wn_pos, keys))

            elem.clear()

        elif tag == "sentence":
            sent_id = f"{doc_id}.s{sent_idx:05d}" if doc_id else f"s{sent_idx:05d}"
            for idx, lemma, wn_pos, keys in targets:
                primary = keys[0] if keys else ""
                all_wn_ids: list[str] = []
                for k in keys:
                    for wn_id in pwn3_sensekey_to_wn(k, lexicon=lexicon):
                        if wn_id not in all_wn_ids:
                            all_wn_ids.append(wn_id)

                yield WSDInstance(
                    instance_id=f"{sent_id}.t{idx:03d}",
                    dataset=dataset,
                    split=split,
                    task=task,
                    lang="en",
                    tokens=list(tokens),
                    pos_tags=list(pos_tags),
                    lemmas=list(lemmas),
                    target_idx=idx,
                    target_lemma=lemma,
                    target_pos=wn_pos,
                    source_sense_id=primary,
                    source_sense_system="pwn_sensekey_3.0",
                    sense_ids_wordnet=all_wn_ids,
                    wordnet_lexicon=lexicon,
                    doc_id=doc_id,
                    sent_id=sent_id,
                )
                emitted += 1
                if limit and emitted >= limit:
                    return
            sent_idx += 1
            elem.clear()

        elif tag == "document":
            elem.clear()


def to_parquet(corpus: str, output_path: Path, ufsac_root: Path,
               lexicon: str = "oewn:2024",
               row_group_size: int = 10_000) -> int:
    """Stream-convert one UFSAC corpus to a single Parquet file.

    Uses a :class:`pyarrow.parquet.ParquetWriter` with chunked writes so
    OMSTI (~1 M rows) and WNGT don't need to be materialized in memory.
    Returns the row count.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    from pywsd_datasets.schema import to_arrow_schema

    schema = to_arrow_schema()
    col_names = [f.name for f in schema]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    batch: dict[str, list] = {c: [] for c in col_names}
    written = 0
    writer: pq.ParquetWriter | None = None

    def flush() -> None:
        nonlocal writer, batch, written
        if not batch[col_names[0]]:
            return
        table = pa.Table.from_pydict(batch, schema=schema)
        if writer is None:
            writer = pq.ParquetWriter(output_path, schema)
        writer.write_table(table)
        written += len(batch[col_names[0]])
        batch = {c: [] for c in col_names}

    try:
        for inst in iter_instances(corpus, ufsac_root, lexicon=lexicon):
            row = inst.to_dict()
            for c in col_names:
                batch[c].append(row[c])
            if len(batch[col_names[0]]) >= row_group_size:
                flush()
        flush()
    finally:
        if writer is not None:
            writer.close()

    return written
