from pprint import pprint
from dataclasses import asdict

def run_multiple_correction_model(source_text):
    from gec_worker import GEC, read_model_config
    from gec_worker import spelling
    from gec_worker.dataclasses import Request
    from gec_worker import multiple_corrections

        # Load grammatical error correction model, use models/GEC-noisy-nmt-ut-config.yaml to use the other model
    model_config = read_model_config('models/GEC-synthetic-pretrain-ut-ft-config.yaml')
    gec = GEC(model_config)

        # Load spelling model
    spelling1 = spelling.Spelling("etnc19_reference_corpus_6000000_web_2019_600000.bin")

        # Make model list and add models
    model_list=multiple_corrections.MultipleCorrections()
    model_list.add_corrector(spelling1)
    model_list.add_corrector(gec)
    
        # Input data and get result
    request = Request(text=source_text, language='et')
    response = model_list.process_request(request)
    pprint(asdict(response))
    return response.corrected_text


if __name__ == '__main__':
    print(run_multiple_correction_model("Juku joksis koolis. Aitüma."))