from pprint import pprint
from dataclasses import asdict


def run_multiple_correction_model(source_text):
    from gec_worker import GEC, read_gec_config
    from gec_worker import Speller, read_speller_config
    from gec_worker import CorrectionList, read_correction_list_config
    from gec_worker.dataclasses import Request
    from gec_worker import MultiCorrector

    # Load grammatical error correction model, use models/GEC-noisy-nmt-ut.yaml to use the other model
    gec_config = read_gec_config('models/GEC-nelb-1.3b.yaml')
    gec = GEC(gec_config)

    # Load spelling model
    speller_config = read_speller_config("models/spell_etnc19_reference_corpus_model_6000000_lines.yaml")
    speller = Speller(speller_config)

    # Load correction list
    correction_list_config = read_correction_list_config('models/correction_list_min3.yaml')
    correction_list = CorrectionList(correction_list_config)

    # Make model list and add models
    multi_corrector = MultiCorrector()
    multi_corrector.add_corrector(correction_list)
    multi_corrector.add_corrector(speller)
    multi_corrector.add_corrector(gec)

    # Input data and get result
    request = Request(text=source_text, language='et')
    response = multi_corrector.process_request(request)
    pprint(asdict(response))
    return response.corrected_text


if __name__ == '__main__':
    print(run_multiple_correction_model("Aga kõik see jõud on suuredes linnades just sellepärast, et väiksetes kohtades on pigem eakad inimesed ja ei ole eriti kultuurielu."))
