# Spelling and Grammatical Error Correction models

Models are either built into the image or can be attached to the
main [grammar-worker](https://github.com/tartunlp/grammar-worker) container by mounting a volume at `/app/models/`. If
the model files are not found, they will be downloaded automatically at startup.

The model files are hosted on HuggingFace.
- Grammatical error correction models
  are [en-et-de-cs-nelb](https://huggingface.co/tartuNLP/en-et-de-cs-nelb/tree/main), [GEC-synthetic-pretrain-ut-ft](https://huggingface.co/tartuNLP/GEC-synthetic-pretrain-ut-ft)
  and [GEC-noisy-nmt-ut](https://huggingface.co/tartuNLP/GEC-noisy-nmt-ut).
- Spell-checking models
  are [etnc19_reference_corpus_model_6000000_lines](https://huggingface.co/Jaagup/etnc19_reference_corpus_model_6000000_lines), [etnc19_web_2019](https://huggingface.co/Jaagup/etnc19_web_2019)
  and [etnc19_reference_corpus_6000000_web_2019_600000](https://huggingface.co/Jaagup/etnc19_reference_corpus_6000000_web_2019_600000).
- For preprocessing, we offer an [error-correction list](https://huggingface.co/Jaagup/errors_corrections_min3) based on L2 learners' reoccurring spelling errors.

Models are saved at `models/{repository owner}/{repository name}`.

## GEC Model configuration

The GEC model should have a matching configuration file with the following keys:

- `huggingface` - name of the model on HuggingFace
- `checkpoint` - path of the model checkpoint file (usually named `checkpoint_best.pt`)
- `dict_dir` - the directory path that contains the model dictionary files (name pattern: `dict.{lang}.txt`)
- `sentencepiece_dir` - the directory that contains sentencepiece models
- `sentencepiece_prefix` - the prefix used on all sentencepiece model files
- `truecase_model` - the path for truecasing model or `no` if no truecasing is used
- `source_language` - input langauge code (as understood by the model)
- `target_language` - output langauge code (as understood by the model)
- `task` - task the model has been trained on (translation, multilingual_translation or translation_multi_simple_epoch)
- `type` - architecture used (nelb, synthetic, modular)

all paths are relative to the root directory of the repository.

### GEC configuration samples

Sample configuration for an Estonian model:

```
huggingface: tartuNLP/GEC-synthetic-pretrain-ut-ft
checkpoint: models/model_name/checkpoint_best.pt
dict_dir: models/model_name/dicts/
sentencepiece_dir: models/model_name/sentencepiece/
sentencepiece_prefix: sp_model
truecase_model: models/model_name/tc-model.tc
source_language: et0
target_language: et
task: translation
type: synthetic
```

The configuration above matches the following folder structure:

```
models
└── tartuNLP
    └── GEC-synthetic-pretrain-ut-ft
        ├── checkpoint_best.pt
        ├── dicts
        │   ├── dict.et0.txt
        │   └── dict.et.txt
        └── sentencepiece
        │   ├── sp_model.et0.model
        │   └── sp_model.et.model
        └── tc-model.tc
```

## Spell-checking Model configuration

The spell-checking model should have a matching configuration file with the following keys:

- `huggingface` - name of the model on HuggingFace
- `model_bin` - path of the model binary file (usually named `{repository_name}.bin`). The path is relative to the root
  directory of the repository.

## Available models

We offer three GEC and three spell-checking models compatible with this repository.

### Grammatical Error Correction

The three GEC models are:

* `en-et-de-cs-nelb` – the model is initialized from the [No Language Left Behind](https://github.com/facebookresearch/fairseq/tree/nllb)(NLLB)
  translation model. It is then further trained with a mix of translation examples and synthetic monolingual error correction examples
   in four languages. Additionally, it is fine-tuned multilingually with error correction examples, including 9,000 in Estonian. 
* `GEC-synthetic-pretrain-ut-ft` – the model is first trained similarly to unidirectional machine translation models first trained
  using a larger synthetic corpus (created from adding simple errors to the monolingual text) and then fine-tuned with
  around 7,000 error correction examples.
* `GEC-noisy-nmt-ut` – the model is built on top of a multilingual machine translation model using monolingual zero-shot
  translation for correcting errors, the GEC performance is improved using translation data with noisy input and
  continuing training with around 7,000 error correction examples.

We strongly recommend using the first model since it achieves significantly higher precision and recall than the other models. 
The second model exhibits slightly higher precision and lower recall compared to the third, whereas the third model is the opposite - 
better recall but worse precision.

### Spell-checking

The three offered spell-checking models have been trained on subsets of the Estonian National Corpus (ENC) 2019:

* `etnc19_reference_corpus_6000000.bin` – a sample retrieved from the Estonian Reference Corpus that represents mostly
  newspaper texts but also fiction, science, and legislation texts from 1990–2008 (6 million sentences, 82.4 million
  words).
* `etnc19_web_2019.bin` – the Estonian Web 2019 corpus that comprises a more diverse selection of texts, from informal
  blog posts and forum discussions to periodicals and educational materials (40.9 million sentences, 512.6 million
  words).
* `etnc19_reference_corpus_6000000_web_2019_600000.bin` – a mix of the Reference Corpus and Web 2019 material in a ratio
  of 10:1, giving emphasis to the more “standardized” texts and using the web texts to add variation to the dataset (6.6
  million sentences, 89.9 million words).

These models achieved the best results when experimenting with different training data. The spelling error detection and correction
performance was first tested on a set of 84 error-annotated Estonian A2–C1-level proficiency examination writings that contain
9,186 words and 309 spelling errors. The test set, model outputs and description of the testing procedure can be found in a separate [repository](https://github.com/tlu-dt-nlp/Spell-testing).

While the model trained on Estonian Web 2019 has the highest error correction precision, its recall is considerably lower than scored by the Reference Corpus model, which, in turn, has
more modest precision. This trade-off is best balanced by the model trained on the 10:1 Reference Corpus + Web sample. All three models outperform the existing rule-based open-source speller Vabamorf and the spell-checker used in MS Word.

Spell-checking results benefit significantly from word replacements based on a list of reoccurring learner errors and expert corrections. The list was compiled on the basis of the Estonian Interlanguage Corpus data (excluding the test material) and contains appr. 3,000 spelling errors. When using list-based preprocessing, our models achieve a higher error correction precision and F<sub>0.5</sub> score compared to Google Docs spelling and grammar checker.

### Evaluation results

The GEC and spell-checking models have been evaluated individually and in combination, using a gold-standard test set of
texts written by learners of Estonian as a second language.

The [error-annotated test material](https://github.com/tlu-dt-nlp/EstGEC-L2-Corpus) includes 156 learner writings taken from
the [Estonian Interlanguage Corpus](https://elle.tlu.ee/tools). These consist of 2,029 sentences, evenly distributed
between the proficiency levels A2, B1, B2, and C1. Adopting the M2 annotation format that indicates the error type,
span, and correction, the following errors are distinguished:

* spelling errors
* capitalization errors
* whitespace errors
* inflectional form (nominal and verb form) errors
* word choice errors
* word order errors
* punctuation choice errors
* missing words and punctuation
* unnecessary words and punctuation

Each sentence can have up to three annotation versions. The version that yields the best match with the correction
output is considered in the evaluation. The M2 Scorer adapted for Estonian can be found [here](https://github.com/TartuNLP/estgec/tree/c3e7bba56f9b20c80f4a63d0e1d5abc17f96aaf9/M2_scorer_est). The results for the GEC models are as follows. 

| System  | Precision  | Recall  | F<sub>0.5</sub>  |
|:---------:|:---:|:----------:|:----------:|
| en-et-de-cs-nelb | 71.92	| 55.44	| 67.88  |
| GEC-synthetic-pretrain-ut-ft  | 66.17 | 42.04 | 59.36 |
| spell v1 + GEC-noisy-nmt-ut  | 56.94 | 45.06 | 54.09 |
| GEC-noisy-nmt-ut  | 56.16 | 43.61 |	53.1 |


The best precision, recall, and F<sub>0.5</sub> score has been achieved by the NELB model, based on the NLLB translation model, 
which achieves a precision of over 70% and recall of over 50%. The Reference Corpus speller model slightly increases the scores for
multilingual NMT based models but its performance is still worse than those incorporating monolingual pre-training.

Considering the NELB results, recall by error type is the best for spelling (81%, missing punctuation (79%), nominal form (69%), verb form (67%) and whitespace errors (61%). About half of the capitalization, unnecessary word and punctuation, word order and word choice errors are also corrected. Recall is the worst for punctuation choice errors (9%).

When all error types are taken into account, the spell-checking models have a low recall, although it improved together with precision in the 2nd iteration (using the error-correction list). The Web 2019 model still has higher precision but the Reference Corpus model yields higher recall and F<sub>0.5</sub> score.

| System  | Precision  | Recall  | F<sub>0.5</sub>  |
|:---------:|:---------:|:---------:|:---------:|
| Reference Corpus model | 58.91 | 7.66 | 25.19 |
| Web 2019 model | 61.50 | 6.29 | 22.32 |
| list + Reference Corpus model | 65.19 | 9.21 | 29.42 |
| list + Web 2019 model | 68.60 | 8.67 | 28.80 |

Currently, only full corrections have been taken into account, disregarding partial corrections of words containing
multiple errors that have to be evaluated qualitatively. Further testing is in progress to validate the models’ ability
to detect and correct errors made by native speakers of Estonian.
