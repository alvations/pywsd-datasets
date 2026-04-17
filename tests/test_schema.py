"""Schema sanity tests."""

from pywsd_datasets.schema import WSDInstance, ARROW_COLUMNS, to_arrow_schema


def test_wsd_instance_roundtrip():
    inst = WSDInstance(
        instance_id="d000.s000.t000",
        dataset="senseval2_aw",
        split="test",
        task="all_words",
        lang="en",
        tokens=["The", "bank", "."],
        target_idx=1,
        target_lemma="bank",
        target_pos="n",
        source_sense_id="bank%1:14:00::",
        source_sense_system="pwn_sensekey_3.0",
        sense_ids_wordnet=["oewn-08420278-n"],
        wordnet_lexicon="oewn:2024",
    )
    d = inst.to_dict()
    assert d["instance_id"] == "d000.s000.t000"
    assert d["sense_ids_wordnet"] == ["oewn-08420278-n"]
    assert d["lang"] == "en"


def test_arrow_schema_matches_dataclass():
    schema = to_arrow_schema()
    cols = [f.name for f in schema]
    assert cols == [name for name, _ in ARROW_COLUMNS]
    # Every WSDInstance field must have a column.
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(WSDInstance)}
    assert field_names == set(cols)
