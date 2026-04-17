"""XL-WSD loader — multilingual (18 languages, BabelNet-keyed).

Pasini, Raganato, Navigli 2021 "XL-WSD: An Extra-Large and
Cross-Lingual Evaluation Framework for Word Sense Disambiguation".

License: CC-BY-NC 4.0. Data distributed via Google Drive from
https://sapienzanlp.github.io/xl-wsd/ — mirror to HF Hub once
licensing-consistent hosting is set up.

XL-WSD shares the Raganato XML format; gold keys are BabelNet IDs
(e.g. ``bn:00009191n``). Use :mod:`pywsd_datasets.mappers.babelnet_to_wn`
to resolve BN → PWN 3.0 → modern lexicon. Without ``bn_to_wn.txt`` the
``sense_ids_wordnet`` field stays empty; rows are still emitted so
coverage_report can flag the gap.

**V1 stub.** Wire once BabelNet mapping file is available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from pywsd_datasets.schema import WSDInstance


XL_WSD_LANGS = [
    "bg", "ca", "da", "de", "el", "en", "es", "et", "eu", "fr",
    "gl", "hr", "hu", "it", "ja", "ko", "nl", "sl", "zh",
]


def iter_instances(lang: str, xl_wsd_root: Path,
                   lexicon: str | None = None) -> Iterator[WSDInstance]:
    raise NotImplementedError(
        "XL-WSD loader: V1 stub. Drop the XL-WSD release in xl_wsd_root and "
        "implement the Raganato-style walk, then call "
        "pywsd_datasets.mappers.babelnet_to_wn for sense-id resolution."
    )
