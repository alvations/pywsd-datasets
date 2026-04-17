"""Raganato loader end-to-end (fetches the bundle on first run, ~1 MB)."""

import pytest

from pywsd_datasets.loaders.raganato import (
    RAGANATO_DATASETS, iter_instances, fetch,
)


def test_dataset_list_non_empty():
    assert "senseval2" in RAGANATO_DATASETS
    assert len(RAGANATO_DATASETS) == 5


def test_fetch_creates_known_directory(tmp_path):
    # Already cached from build step — fetch should be a no-op; we just
    # verify the returned path contains the expected sub-dirs.
    root = fetch()
    for name in RAGANATO_DATASETS:
        assert (root / name).is_dir(), f"missing {name} sub-dir under {root}"


def test_senseval2_first_record_well_formed(wordnet):
    it = iter_instances("senseval2")
    inst = next(it)
    assert inst.dataset == "senseval2_aw"
    assert inst.split == "test"
    assert inst.lang == "en"
    assert inst.source_sense_system == "pwn_sensekey_3.0"
    assert inst.target_pos in {"n", "v", "a", "r"}
    # Most PWN 3.0 keys should resolve under OEWN 2024.
    assert inst.sense_ids_wordnet, \
        f"expected oewn id for {inst.source_sense_id}"


@pytest.mark.parametrize("name", list(RAGANATO_DATASETS))
def test_every_raganato_dataset_yields_rows(wordnet, name):
    count = 0
    for inst in iter_instances(name):
        count += 1
        if count > 5:
            break
    assert count > 0, f"{name} produced no rows"
