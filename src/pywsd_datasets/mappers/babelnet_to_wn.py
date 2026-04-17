"""BabelNet → WordNet sense-key mapping.

XL-WSD and SemEval-2013/2015 multilingual tracks use BabelNet IDs
(``bn:00009191n``) as gold senses. BabelNet ships a ``bn_to_wn.txt``
(or equivalent) bridge file mapping each BN synset to a PWN 3.0 sense
key (or offset), from which we chain through :mod:`pwn3_to_oewn` to
reach modern wn synset IDs.

**V1 is a stub.** The actual mapping file is distributed with
BabelNet (academic login required) and is large (~300 MB). The V1
loader for XL-WSD therefore emits rows with the BabelNet ID in
``source_sense_id`` and an empty ``sense_ids_wordnet`` list; the
coverage report flags the gap. Populate by dropping ``bn_to_wn.txt``
into ``data/external/`` and calling :func:`load_bn_to_pwn3_map`.
"""

from __future__ import annotations

from pathlib import Path


_CACHE: dict[str, str] | None = None


def load_bn_to_pwn3_map(path: str | Path) -> dict[str, str]:
    """Load a BabelNet-ID → PWN 3.0 sensekey mapping from a TSV/TXT file.

    Expected format (one mapping per line)::

        bn:00009191n <TAB> bank%1:14:00::

    Falls back to offset-based rows if sense keys aren't present.
    """
    global _CACHE
    mapping: dict[str, str] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            bn_id = parts[0]
            target = parts[1]
            mapping[bn_id] = target
    _CACHE = mapping
    return mapping


def bn_to_wn_ids(bn_id: str, lexicon: str = "oewn:2024") -> list[str]:
    """Map a BabelNet synset ID to modern wn synset IDs in *lexicon*.

    Returns an empty list if no mapping file has been loaded or no hit.
    """
    if not _CACHE:
        return []
    pwn3 = _CACHE.get(bn_id)
    if not pwn3:
        return []
    from pywsd_datasets.mappers.pwn3_to_oewn import pwn3_sensekey_to_wn
    return pwn3_sensekey_to_wn(pwn3, lexicon=lexicon)
