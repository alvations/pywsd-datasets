"""XL-WSD loader — multilingual (18 languages).

**Status: not implemented in v0.2.** Called explicitly raises
``NotImplementedError`` so nothing silently degrades.

Why we skipped it
-----------------

XL-WSD (Pasini, Raganato, Navigli 2021) uses BabelNet synset IDs as
gold labels (e.g. ``bn:00009191n``). Resolving those to modern ``wn``
lexicon synset IDs requires a BabelNet → PWN 3.0 bridge file that is
distributed only to BabelNet academic licensees. Without that file,
rows would ship with empty ``sense_ids_wordnet`` and the coverage
report would drop to ~0 % — worse than the current state.

Additionally, the CC-BY-NC 4.0 license on XL-WSD means we cannot
redistribute the gold files in a repo that advertises MIT (loader-only
is acceptable, but still needs the BabelNet mapping to be useful).

Resurrecting it
---------------

1. Acquire a BabelNet 4.x academic license + the ``bn_to_wn.txt``
   mapping file.
2. Load the mapping at build time with
   :func:`pywsd_datasets.mappers.babelnet_to_wn.load_bn_to_pwn3_map`.
3. Use the OMW lexicon matching each target language via
   :func:`pywsd_datasets.mappers.omw_lookup.lexicon_for`.
4. Call the PWN 3.0 → lexicon mapper
   (:func:`pywsd_datasets.mappers.pwn3_to_oewn.pwn3_sensekey_to_wn`)
   with ``lexicon=lexicon_for(lang)``.

See ``loaders/raganato.py`` for the XML walking pattern; XL-WSD shares
the Raganato format.

References
----------
* Pasini, Raganato, Navigli (2021). *XL-WSD: An Extra-Large and
  Cross-Lingual Evaluation Framework for Word Sense Disambiguation.*
  AAAI.
* https://sapienzanlp.github.io/xl-wsd/
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
        "XL-WSD is not implemented in pywsd-datasets v0.2. It requires "
        "the BabelNet → PWN 3.0 bridge file (academic license only) and "
        "is CC-BY-NC, so we do not redistribute. See the module docstring "
        "in pywsd_datasets/loaders/xl_wsd.py for how to revive it."
    )
