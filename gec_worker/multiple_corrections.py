from typing import List
from .utils import sentence_tokenize, generate_spans
from .dataclasses import Response, Request
import logging
logger = logging.getLogger(__name__)
import warnings
import itertools

warnings.filterwarnings('ignore', '.*__floordiv__*', )

class MultipleCorrections:
    correctors=[]
    def __init__(self):
        pass

    def add_corrector(self, corrector):
       self.correctors.append(corrector)

    def correct(self, sentences: List[str]) -> List[str]:
        temp=sentences
        for corrector in self.correctors:
            temp=corrector.correct(temp)
        return temp

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
