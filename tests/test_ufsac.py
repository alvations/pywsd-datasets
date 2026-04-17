"""UFSAC loader tests — skipped if the UFSAC tarball isn't unpacked locally."""

from pathlib import Path

import pytest

from pywsd_datasets.loaders.ufsac import (
    UFSAC_CORPORA, iter_instances, _penn_to_wn_pos,
)


UFSAC_ROOT_ENV = "PYWSD_DATASETS_UFSAC_ROOT"
_DEFAULT_ROOT = Path.home() / ".cache/pywsd-datasets/ufsac/ufsac-public-2.1"


def _ufsac_root() -> Path:
    import os
    env = os.environ.get(UFSAC_ROOT_ENV)
    if env:
        return Path(env)
    return _DEFAULT_ROOT


pytestmark = pytest.mark.skipif(
    not _ufsac_root().exists(),
    reason=f"UFSAC not unpacked at {_ufsac_root()} "
           f"(set {UFSAC_ROOT_ENV} to override)",
)


def test_corpus_list():
    assert "semcor" in UFSAC_CORPORA
    assert "wngt" in UFSAC_CORPORA
    assert "masc" in UFSAC_CORPORA


@pytest.mark.parametrize("penn,wn", [
    ("NN", "n"), ("NNS", "n"), ("NNP", "n"),
    ("VB", "v"), ("VBD", "v"), ("VBG", "v"),
    ("JJ", "a"), ("JJR", "a"),
    ("RB", "r"), ("RBR", "r"),
    ("DT", ""), ("IN", ""), ("", ""),
])
def test_penn_to_wn_pos(penn, wn):
    assert _penn_to_wn_pos(penn) == wn


def test_semeval2007_t17_first_records(wordnet):
    it = iter_instances("semeval2007_t17", _ufsac_root())
    inst = next(it)
    assert inst.dataset == "semeval2007_t17_ls"
    assert inst.source_sense_system == "pwn_sensekey_3.0"
    assert inst.target_pos in {"n", "v", "a", "r"}
    # Most PWN 3.0 keys should resolve under OEWN 2024.
    assert inst.sense_ids_wordnet, \
        f"expected oewn id for {inst.source_sense_id}"


def test_senseval2_ls_test_streams(wordnet):
    """Lexical-sample corpora are larger; verify iterparse streaming works."""
    count = 0
    for inst in iter_instances("senseval2_ls_test", _ufsac_root()):
        count += 1
        if count > 20:
            break
    assert count > 0
