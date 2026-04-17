"""UFSAC v2.1 loader — SemCor, WNGT, MASC, OMSTI, Senseval lex-sample.

Unification Framework for Sense Annotated Corpora (Vial, Lecouteux,
Schwab 2018). MIT-licensed; unifies 15+ sense-tagged English corpora
with all keys remapped to WN 3.0.

Upstream distribution is a single Google Drive zip (~2 GB unpacked):
    https://github.com/getalp/UFSAC  (Drive link in the README)

Because the URL is not HTTP-fetchable, this loader takes an
already-downloaded copy and normalizes it. Mirror the zip to the
repo's HF Hub release assets once bandwidth policy is decided.

**V1 stub.** Implementation follows the same pattern as
:mod:`pywsd_datasets.loaders.raganato` — UFSAC XML has the structure
``<corpus><document><paragraph><sentence><word lemma= pos= wn30_key=>
TEXT</word></sentence>…``. Populate when the first UFSAC zip is
mirrored.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from pywsd_datasets.schema import WSDInstance


UFSAC_CORPORA = [
    "semcor",
    "wngt",
    "masc",
    "omsti",
    "senseval2_ls",
    "senseval3_ls",
    "semeval2007_t17",
    "semeval2013_t12",
    "semeval2015_t13",
]


def iter_instances(corpus: str, ufsac_root: Path,
                   lexicon: str = "oewn:2024") -> Iterator[WSDInstance]:
    """Yield WSDInstance records. *ufsac_root* points at the unpacked zip."""
    raise NotImplementedError(
        "UFSAC loader: V1 stub. Unpack UFSAC 2.1 into a directory, then "
        "implement the XML walk here. See raganato.py for the pattern."
    )
