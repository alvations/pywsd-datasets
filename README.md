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
  - semcor
  - semeval
  - senseval
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
  - config_name: en-semcor
    data_files:
      - split: train
        path: data/en-semcor/train.parquet
  - config_name: en-wngt
    data_files:
      - split: train
        path: data/en-wngt/train.parquet
  - config_name: en-masc
    data_files:
      - split: train
        path: data/en-masc/train.parquet
  - config_name: en-senseval2_ls
    data_files:
      - split: train
        path: data/en-senseval2_ls/train.parquet
      - split: test
        path: data/en-senseval2_ls/test.parquet
  - config_name: en-senseval3_ls
    data_files:
      - split: train
        path: data/en-senseval3_ls/train.parquet
      - split: test
        path: data/en-senseval3_ls/test.parquet
  - config_name: en-semeval2007_t17_ls
    data_files:
      - split: test
        path: data/en-semeval2007_t17_ls/test.parquet
---

# pywsd-datasets

Unified Word Sense Disambiguation benchmark datasets, normalized to **modern
`wn` lexicon sense IDs** (`oewn:2024` for English, OMW for other languages).

Companion to [pywsd](https://pypi.org/project/pywsd/) ≥ 1.3.0.

## What's shipped (v0.2)

**English, test-only Raganato all-words benchmark:**

| Config                | Instances | OEWN 2024 coverage |
|-----------------------|-----------|--------------------|
| `en-senseval2-aw`     | 2,282     | 99.43 %            |
| `en-senseval3-aw`     | 1,850     | 99.51 %            |
| `en-semeval2007-aw`   | 455       | 99.78 %            |
| `en-semeval2013-aw`   | 1,644     | 100.00 %           |
| `en-semeval2015-aw`   | 1,022     | 99.32 %            |

**English, training corpora (via UFSAC v2.1):**

| Config                    | Split | OEWN 2024 coverage |
|---------------------------|-------|--------------------|
| `en-semcor`               | train | see coverage_report |
| `en-wngt`                 | train | see coverage_report |
| `en-masc`                 | train | see coverage_report |
| `en-senseval2_ls`         | train + test | lexical-sample |
| `en-senseval3_ls`         | train + test | lexical-sample |
| `en-semeval2007_t17_ls`   | test  | lexical-sample |

Run `python -m pywsd_datasets.scripts.coverage_report` locally to get
up-to-date OEWN resolution rates after rebuilding.

## Install

```bash
pip install pywsd-datasets
```

## Use via HuggingFace `datasets`

```python
from datasets import load_dataset

# Raganato all-words evaluation set
ds = load_dataset("alvations/pywsd-datasets", "en-senseval2-aw")

# SemCor training data
ds = load_dataset("alvations/pywsd-datasets", "en-semcor")

ds["test"][0] if "test" in ds else ds["train"][0]
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
from pywsd_datasets.loaders.raganato import iter_instances as iter_raganato
from pywsd_datasets.loaders.ufsac import iter_instances as iter_ufsac

for inst in iter_raganato("senseval2"):
    print(inst.target_lemma, inst.sense_ids_wordnet)

for inst in iter_ufsac("semcor", "/path/to/ufsac-public-2.1"):
    print(inst.target_lemma, inst.sense_ids_wordnet)
```

## Rebuild locally

```bash
pip install pywsd-datasets[dev]

# Raganato only (always works, ~1 MB fetch from our GH release mirror)
python -m pywsd_datasets.scripts.build_all

# With UFSAC corpora — download ufsac-public-2.1 separately (see below)
python -m pywsd_datasets.scripts.build_all \
    --ufsac-root ~/.cache/pywsd-datasets/ufsac/ufsac-public-2.1

# Coverage report across every built parquet:
python -m pywsd_datasets.scripts.coverage_report
```

### UFSAC download

UFSAC v2.1 is distributed as a single Google Drive tarball
(`ufsac-public-2.1.tar.xz`, ~196 MB). Fetch with `gdown`:

```bash
pip install gdown
mkdir -p ~/.cache/pywsd-datasets/ufsac
gdown 'https://drive.google.com/uc?id=1kwBMIDBTf6heRno9bdLvF-DahSLHIZyV' \
    -O ~/.cache/pywsd-datasets/ufsac/ufsac-public-2.1.tar.xz
cd ~/.cache/pywsd-datasets/ufsac && tar -xf ufsac-public-2.1.tar.xz
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

## Multilingual / XL-WSD / BabelNet — deferred

`loaders/xl_wsd.py` exists as a stub and raises `NotImplementedError`.
`mappers/babelnet_to_wn.py` is similarly unused. **Why:**

* XL-WSD uses BabelNet synset IDs as gold labels; resolving them to
  modern `wn` lexicon IDs requires the BabelNet → PWN 3.0 bridge file,
  which is distributed **only with a BabelNet academic license**.
* XL-WSD itself is CC-BY-NC 4.0 — we don't redistribute the data.

Reviving this path requires (a) a BabelNet license, (b) loading
`bn_to_wn.txt` via `babelnet_to_wn.load_bn_to_pwn3_map()`, (c) selecting
per-language OMW lexicons via `mappers.omw_lookup.lexicon_for(lang)`,
then (d) chaining through `pwn3_to_oewn.pwn3_sensekey_to_wn(key, lexicon=...)`.
All four pieces are in place — wiring them is blocked on the BabelNet
mapping file. See the module docstrings for details.

## Roadmap

* **v0.2** (this release): Raganato all-words evaluation + UFSAC training
  corpora (SemCor, WNGT, MASC, Senseval lexical-sample).
* **v0.3** (planned): WiC (CC-BY-NC — loader-only), CoarseWSD-20.
* **Deferred:** XL-WSD multilingual (needs BabelNet academic license).

## Citation

If you use these datasets please cite the original sources:

* Raganato, Camacho-Collados, Navigli (2017). *Word Sense Disambiguation:
  A Unified Evaluation Framework and Empirical Comparison.* EACL.
* Vial, Lecouteux, Schwab (2018). *UFSAC: Unification of Sense Annotated
  Corpora and Tools.* LREC.
* Plus the specific evaluation or training set paper (Senseval-2 / 3,
  SemEval-2007 T17, SemEval-2013 T12, SemEval-2015 T13, SemCor,
  WNGT/Princeton Gloss Corpus, MASC).

## License

MIT for the code. Each dataset keeps its original license — see the source
papers. Raganato bundle and SemEval shared-task data are
research-unrestricted; UFSAC is MIT.

## Sense-ID mapping details

PWN 3.0 sense keys are resolved against OEWN 2024 via
[`wn.compat.sensekey`](https://github.com/goodmami/wn). The few percent of
keys that fail to resolve are typically WN 3.0 synsets that OEWN split,
merged, or removed — those rows ship with an empty `sense_ids_wordnet` list
so the coverage report can flag them. Background:

* Kaf (2023). *Mapping Wordnets on the Fly with Permanent Sense Keys.*
  arXiv:2303.01847.

## Known issues

* The upstream Raganato zip at `http://lcl.uniroma1.it/wsdeval/` serves a
  mismatched TLS cert; our loader prefers the mirror on this repo's
  GitHub release assets and falls back to the original URL over HTTP.
* UFSAC v2.1 is distributed as a Google Drive tarball; the loader assumes
  you have it unpacked locally. A future release may mirror it.
