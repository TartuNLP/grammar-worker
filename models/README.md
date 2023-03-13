# Grammatical error correction models

Models are either built into the image or can be attached to the
main [grammar-worker](https://github.com/tartunlp/grammar-worker) container by mounting a volume at `/app/models/`. When
running locally, they should be placed in the `models/` directory.

You can download model files from the [releases page](https://github.com/TartuNLP/grammar-worker/releases).

## Model configuration

By default, the application looks for a `config.yaml` file in the `/models` directory
of the repository. This file should contain the following keys:

- `language` - 2-letter ISO language code
- `checkpoint` - path of the model checkpoint file (usually named `checkpoint_best.pt`)
- `dict_dir` - the directory path that contains the model dictionary files (name pattern: `dict.{lang}.txt`)
- `sentencepiece_dir` - the directory that contains sentencepiece models
- `sentencepiece_prefix` - the prefix used on all sentencepiece model files
- `truecase_model` - the path for truecasing model
- `source_language` - input langauge code (as understood by the model)
- `target_language` - output langauge code (as understood by the model)
- `task` - task the model has been trained on (translation or multilingual_translation)

### Configuration samples

Sample configuration for an Estonian model:

```
language: et
checkpoint: models/model_name/checkpoint_best.pt
dict_dir: models/model_name/dicts/
sentencepiece_dir: models/model_name/sentencepiece/
sentencepiece_prefix: sp_model
truecase_model: models/model_name/tc-model.tc
source_language: et0
target_language: et
task: translation
```

The configuration above matches the following folder structure:

```
models
── model_name
   ├── checkpoint_best.pt
   ├── dicts
   │   ├── dict.et0.txt
   │   └── dict.et.txt
   └── sentencepiece
       ├── sp_model.et0.model
       └── sp_model.et.model
   └── tc-model.tc
```

## Available models

The two offered GEC models are:

* GEC-synthetic-pretrain-ut-ft – model is first trained similarly to unidirectional machine translation models first using a larger synthetic corpus (created from adding simple errors to the monolingual text) and then fine-tuned with around 7,000 error correction examples. 
* GEC-noisy-nmt-ut – model is built on top of a multilingual machine translation model using monolingual zero-shot translation for correcting errors, the GEC performance is improved using translation data with noisy input and continuing training with around 7,000 error correction examples.

The first model exhibits slightly higher precision and lower recall, whereas the second model is the opposite - better recall but worse precision.

The three offered spell-checking models have been trained on subsets of the Estonian National Corpus (ENC) 2019:

* etnc19_reference_corpus_6000000.bin – a sample retrieved from the Estonian Reference Corpus that represents mostly newspaper texts but also fiction, science, and legislation texts from 1990–2008 (6 million sentences, 82.4 million words).
* etnc19_web_2019.bin – the Estonian Web 2019 corpus that comprises a more diverse selection of texts, from informal blog posts and forum discussions to periodicals and educational materials (40.9 million sentences, 512.6 million words).
* etnc19_reference_corpus_6000000_web_2019_600000.bin – a mix of the Reference Corpus and Web 2019 material in a ratio of 10:1, giving emphasis to the more “standardized” texts and using the web texts to add variation to the dataset (6.6 million sentences, 89.9 million words).

These models achieved the highest F0.5 score when experimenting with different training data. The spelling correction performance was tested on a set of 84 error-annotated Estonian A2–C1-level proficiency examination writings that contain 9,186 words and 309 spelling errors in total. Error correction precision was measured based on the top-ranked suggestion.

While the model trained on Estonian Web 2019 had the highest precision (74.4%) and F0.5 score (69.1), its recall (53.7%) was considerably lower than scored by the model trained on the Reference Corpus sample (67.0%), which, in turn, had a more modest precision (68.4%) and F0.5 score (68.1). This trade-off was best balanced by the model trained on the 10:1 Reference Corpus + Web sample, scoring 69.6% in precision and 60.2% in recall (F0.5 = 67.5). All three models outperformed the existing rule-based open-source speller Vabamorf in terms of precision (45.0%) and F0.5 score (48.4), whereas the latter had a higher recall (69.3%).

### System Evaluation

The GEC and spell-checking models have been evaluated individually and in combination, using a gold-standard test set of texts written by learners of Estonian as a second language.

The error-annotated test material includes 156 learner writings taken from the Estonian Interlanguage Corpus. These consist of 2,029 sentences, evenly distributed between the proficiency levels A2, B1, B2, and C1. Adopting the M2 annotation format that indicates the error type, span, and correction, the following errors are distinguished:

* spelling errors
* capitalization errors
* whitespace errors
* inflectional form (nominal and verb form) errors
* word choice errors
* word order errors
* punctuation choice errors
* missing words and punctuation
* unnecessary words and punctuation

Each sentence can have up to three annotation versions. The version that yields the best match with the correction output is considered in evaluation.
The best F0.5 score have been achieved by the GEC-synthetic-pretrain-ut-ft model (56.8) and the combination of the GEC-noisy-nmt-ut model and the Reference Corpus spell-checking model, using the spelling correction output as input for GEC (52.2). The GEC-synthetic-pretrain-ut-ft  model has a higher precision (64.6%) and a lower recall (38.4%), which are not significantly affected by pre-processing the input text with a speller model. On the other hand, the GEC-noisy-nmt-ut model’s precision (55.0%) and recall (39.8%) are improved by additional spell-checking, especially the Reference Corpus model that increases the precision to 55.9% and recall to 41.2%.

Currently, only full corrections have been taken into account, disregarding partial corrections of words containing multiple errors that have to be evaluated qualitatively. Further testing is in progress to validate the models’ ability to detect and correct different error types as well as errors made by native speakers of Estonian.
