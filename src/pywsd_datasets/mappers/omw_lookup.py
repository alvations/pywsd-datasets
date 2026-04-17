"""Per-language OMW lexicon selector.

Maps ISO-639-1 language codes to the canonical OMW lexicon specifier
that ``wn>=1.0`` knows how to open. Used by multilingual loaders
(XL-WSD, SemEval-2013/2015, etc.) to pick the right sense space per
row.

See ``wn.lexicons()`` at runtime for the authoritative list on the
installed wordnet database.
"""

from __future__ import annotations

# ISO-639-1 → canonical OMW lexicon specifier.
# Extend as needed; stubs only cover the languages XL-WSD ships.
OMW_LEXICON: dict[str, str] = {
    "en": "oewn:2024",
    "it": "omw-it:1.4",
    "de": "omw-de:1.4",
    "es": "omw-es:1.4",
    "fr": "omw-fr:1.4",
    "ja": "omw-ja:1.4",
    "nl": "omw-nl:1.4",
    "zh": "omw-cmn:1.4",
    "ca": "omw-ca:1.4",
    "eu": "omw-eu:1.4",
    "gl": "omw-gl:1.4",
    "sl": "omw-sl:1.4",
    "pt": "omw-pt:1.4",
    "bg": "omw-bg:1.4",
    "da": "omw-da:1.4",
    "el": "omw-el:1.4",
    "hr": "omw-hr:1.4",
    "ko": "omw-ko:1.4",
}


def lexicon_for(lang: str) -> str:
    """Return the wn lexicon specifier for *lang*; raise if unknown."""
    try:
        return OMW_LEXICON[lang]
    except KeyError as e:
        raise ValueError(
            f"no OMW lexicon registered for lang={lang!r}. "
            f"Known: {sorted(OMW_LEXICON)}"
        ) from e
