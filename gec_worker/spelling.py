import jamspell

import itertools
import logging
import os
from typing import List
import warnings

from .dataclasses import Response, Request
from .utils import sentence_tokenize, generate_spans

logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore', '.*__floordiv__*', )



class Spelling:
    model = None

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.corrector=jamspell.TSpellCorrector()
        self.corrector.LoadLangModel("models/spellmodels/"+self.model_name)
 
    def correct(self, sentences: List[str]) -> List[str]:
        return [self.corrector.FixFragment(sentence) for sentence in sentences]

    def process_request(self, request: Request) -> Response:
        sentences, delimiters = sentence_tokenize(
            request.text
        )
        predictions = [correction.strip() if sentences[idx] != '' else '' for idx, correction in enumerate(
            self.correct(sentences))]

        corrected = ''.join(itertools.chain.from_iterable(zip(delimiters, predictions))) + delimiters[-1]
        logger.debug(corrected)

        corrections = generate_spans(sentences, predictions, delimiters)
        response = Response(corrections=corrections, original_text=request.text, corrected_text=corrected)

        logger.debug(response)

        return response
