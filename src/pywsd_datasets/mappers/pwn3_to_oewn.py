"""Map Princeton WordNet 3.0 sense keys to modern ``wn`` synset IDs.

Two hops, but the library provides both:

1. ``wn.compat.sensekey.sense_getter(lexicon)`` resolves a PWN 3.0 sense
   key to a :class:`wn.Sense` object inside *lexicon* (OEWN for English,
   OMW for other languages), if the lexicon exposes sensekey metadata.
2. ``sense.synset()`` gives us the synset, and its ``.id`` is the
   modern-wn identifier we want to store.

Expected coverage: ~98% for PWN 3.0 keys against OEWN 2024 (Kaf 2023,
arXiv:2303.01847). Unresolved keys are logged; the loader still emits
the row with an empty ``sense_ids_wordnet`` list so the coverage report
can flag the gap.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=4)
def _get_sense_getter(lexicon: str):
    """Cache the per-lexicon getter — constructing one is not cheap."""
    from wn.compat.sensekey import sense_getter
    return sense_getter(lexicon)


def pwn3_sensekey_to_wn(sensekey: str, lexicon: str = "oewn:2024") -> list[str]:
    """Return a list of modern-wn synset IDs for *sensekey*.

    Returns an empty list if the key cannot be resolved (synset removed,
    merged, or lexicon missing the sensekey metadata).
    """
    if not sensekey:
        return []
    get = _get_sense_getter(lexicon)
    try:
        sense = get(sensekey)
    except Exception:
        return []
    if sense is None:
        return []
    try:
        return [sense.synset().id]
    except Exception:
        return []


def batch_resolve(sensekeys: list[str], lexicon: str = "oewn:2024") -> list[list[str]]:
    """Vectorized convenience wrapper around :func:`pwn3_sensekey_to_wn`."""
    return [pwn3_sensekey_to_wn(k, lexicon) for k in sensekeys]
