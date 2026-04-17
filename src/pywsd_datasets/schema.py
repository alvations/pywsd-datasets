"""Unified schema for a sense-disambiguation instance.

Flat JSON / Arrow-friendly. The same record works for English (OEWN) and
any OMW language; ``wordnet_lexicon`` identifies the target sense space.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class WSDInstance:
    # Identity ---------------------------------------------------------------
    instance_id: str                    # globally-unique per row
    dataset: str                        # "senseval2_aw", "semcor", "xlwsd_it", ...
    split: str                          # "train" | "validation" | "test"
    task: str                           # "all_words" | "lexical_sample" | "wic" | "coarse"
    lang: str                           # "en", "it", "de", ...

    # Textual context --------------------------------------------------------
    tokens: list[str] = field(default_factory=list)
    pos_tags: list[str] = field(default_factory=list)      # optional, Penn-style or UD; may be empty
    lemmas: list[str] = field(default_factory=list)        # optional

    # Target word ------------------------------------------------------------
    target_idx: int = -1                # index into tokens
    target_lemma: str = ""
    target_pos: str = ""                # 'n' | 'v' | 'a' | 'r'

    # Source sense annotation ------------------------------------------------
    # What the original gold file said, untouched.
    source_sense_id: str = ""           # e.g. "bank%1:14:00::" or "bn:00009191n"
    source_sense_system: str = ""       # "pwn_sensekey_3.0" | "bn:4.0" | "oewn_id" | ...

    # Normalized sense(s) in the modern wn target lexicon --------------------
    # List-valued to tolerate instances tagged with multiple senses in the
    # original gold, or post-mapping splits.
    sense_ids_wordnet: list[str] = field(default_factory=list)
    wordnet_lexicon: str = ""           # "oewn:2024" | "omw-it:1.4" | ...

    # Provenance -------------------------------------------------------------
    doc_id: str = ""
    sent_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Arrow/Parquet schema — mirrors the dataclass. Ordered for stable columnar
# output so two builds diff cleanly.
ARROW_COLUMNS: list[tuple[str, str]] = [
    ("instance_id", "string"),
    ("dataset", "string"),
    ("split", "string"),
    ("task", "string"),
    ("lang", "string"),
    ("tokens", "list<string>"),
    ("pos_tags", "list<string>"),
    ("lemmas", "list<string>"),
    ("target_idx", "int32"),
    ("target_lemma", "string"),
    ("target_pos", "string"),
    ("source_sense_id", "string"),
    ("source_sense_system", "string"),
    ("sense_ids_wordnet", "list<string>"),
    ("wordnet_lexicon", "string"),
    ("doc_id", "string"),
    ("sent_id", "string"),
]


def to_arrow_schema():
    """Build the pyarrow schema for WSDInstance records."""
    import pyarrow as pa

    type_map = {
        "string": pa.string(),
        "int32": pa.int32(),
        "list<string>": pa.list_(pa.string()),
    }
    return pa.schema([(name, type_map[t]) for name, t in ARROW_COLUMNS])
