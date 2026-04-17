"""Sense-key → OEWN 2024 mapping sanity."""

import pytest

from pywsd_datasets.mappers.pwn3_to_oewn import pwn3_sensekey_to_wn


def test_unknown_key_returns_empty_list(wordnet):
    assert pwn3_sensekey_to_wn("") == []
    assert pwn3_sensekey_to_wn("not_a_real_sense%99:99:99::") == []


def test_common_english_key_resolves(wordnet):
    # "dog" has a well-known PWN 3.0 sense key.
    ids = pwn3_sensekey_to_wn("dog%1:05:00::")
    assert ids, "expected at least one oewn synset id"
    assert ids[0].startswith("oewn-") and ids[0].endswith("-n")


@pytest.mark.parametrize("key", [
    "bank%1:14:00::",    # financial institution
    "bank%1:17:01::",    # river bank
    "art%1:09:00::",     # artistic skill
    "run%2:38:04::",     # "run" as a verb
])
def test_sample_keys_round_trip(wordnet, key):
    ids = pwn3_sensekey_to_wn(key)
    assert ids, f"{key} should resolve under oewn:2024"
