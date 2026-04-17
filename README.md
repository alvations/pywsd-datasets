---
pretty_name: pywsd-datasets
license: mit
task_categories:
  - token-classification
language:
  - en
tags:
  - word-sense-disambiguation
  - wsd
  - wordnet
  - oewn
  - semeval
  - senseval
size_categories:
  - 1K<n<10K
configs:
  - config_name: en-senseval2-aw
    data_files:
      - split: test
        path: data/en-senseval2-aw/test.parquet
  - config_name: en-senseval3-aw
    data_files:
      - split: test
        path: data/en-senseval3-aw/test.parquet
  - config_name: en-semeval2007-aw
    data_files:
      - split: test
        path: data/en-semeval2007-aw/test.parquet
  - config_name: en-semeval2013-aw
    data_files:
      - split: test
        path: data/en-semeval2013-aw/test.parquet
  - config_name: en-semeval2015-aw
    data_files:
      - split: test
        path: data/en-semeval2015-aw/test.parquet
---

# pywsd-datasets

Unified Word Sense Disambiguation benchmark datasets, normalized to **modern
`wn` lexicon sense IDs** (`oewn:2024` for English, OMW for other languages).

Companion to [pywsd](https://pypi.org/project/pywsd/) ≥ 1.3.0.

## What's in v0.1 (English-only, expanding)

| Config                | Source                 | Instances | OEWN 2024 coverage |
|-----------------------|------------------------|-----------|--------------------|
| `en-senseval2-aw`     | Raganato et al. 2017   | 2,282     | 99.43 %            |
| `en-senseval3-aw`     | Raganato et al. 2017   | 1,850     | 99.51 %            |
| `en-semeval2007-aw`   | Raganato et al. 2017   | 455       | 99.78 %            |
| `en-semeval2013-aw`   | Raganato et al. 2017   | 1,644     | 100.00 %           |
| `en-semeval2015-aw`   | Raganato et al. 2017   | 1,022     | 99.32 %            |
| **Total**             |                        | **7,253** | **99.59 %**        |

## Install

```bash
pip install pywsd-datasets
```

## Use via HuggingFace `datasets`

```python
from datasets import load_dataset
ds = load_dataset("alvations/pywsd-datasets", "en-senseval2-aw")
ds["test"][0]
# {'instance_id': 'd000.s000.t000', 'dataset': 'senseval2_aw',
#  'split': 'test', 'lang': 'en',
#  'tokens': ['The', 'art', 'of', 'change-ringing', ...],
#  'target_idx': 1, 'target_lemma': 'art', 'target_pos': 'n',
#  'source_sense_id': 'art%1:09:00::',
#  'source_sense_system': 'pwn_sensekey_3.0',
#  'sense_ids_wordnet': ['oewn-05646832-n'],
#  'wordnet_lexicon': 'oewn:2024', ...}
```

## Use via the loader package

```python
from pywsd_datasets.loaders.raganato import iter_instances
for inst in iter_instances("senseval2"):
    print(inst.target_lemma, inst.sense_ids_wordnet)
```

## Rebuild locally

```bash
pip install pywsd-datasets[dev]
python -m pywsd_datasets.scripts.build_all              # parquet in data/
python -m pywsd_datasets.scripts.coverage_report        # OEWN 2024 resolution %
```

## Schema

Every row follows [`WSDInstance`](src/pywsd_datasets/schema.py):

```
instance_id, dataset, split, task, lang,
tokens[], pos_tags[], lemmas[],
target_idx, target_lemma, target_pos,
source_sense_id, source_sense_system,
sense_ids_wordnet[], wordnet_lexicon,
doc_id, sent_id
```

`sense_ids_wordnet` is list-valued to handle multi-gold instances and any
PWN-3.0 key that splits into multiple OEWN 2024 synsets.

## Roadmap

* **v0.2** — UFSAC corpora (SemCor, WNGT, MASC, OMSTI, Senseval lexical-sample).
* **v0.3** — WiC (CC-BY-NC), CoarseWSD-20.
* **v0.4** — XL-WSD multilingual via BabelNet → WordNet → OMW. Initial
  languages: it, de, fr, es, ja (then the full XL-WSD 18 over time).

Loader stubs already live under `src/pywsd_datasets/loaders/` for ufsac
and xl_wsd.

## Citation

If you use these datasets please cite the original sources:

* Raganato, Camacho-Collados, Navigli (2017). *Word Sense Disambiguation:
  A Unified Evaluation Framework and Empirical Comparison.* EACL.
* Plus the paper for whichever specific evaluation set you use
  (Senseval-2 / 3, SemEval-2007 T17, SemEval-2013 T12, SemEval-2015 T13).

## License

MIT for the code. Each dataset keeps its original license — see the source
papers. Raganato bundle and SemEval shared-task data are research-unrestricted.

## Sense-ID mapping details

PWN 3.0 sense keys are resolved against OEWN 2024 via
[`wn.compat.sensekey`](https://github.com/goodmami/wn). The few percent of
keys that fail to resolve are typically WN 3.0 synsets that OEWN split,
merged, or removed — those rows ship with an empty `sense_ids_wordnet` list
so the coverage report can flag them. Background:

* Kaf (2023). *Mapping Wordnets on the Fly with Permanent Sense Keys.*
  arXiv:2303.01847.

## Known issues

* `lcl.uniroma1.it` serves a mismatched TLS cert; the loader fetches the
  Raganato bundle over HTTP. When this repo matures we'll mirror the zip
  to the HF Hub release assets.
* UFSAC v2.1 distribution is a Google Drive zip last updated 2018; same
  mirror plan applies once licensing is confirmed.
