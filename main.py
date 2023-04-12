import threading
from argparse import ArgumentParser, FileType

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from gec_worker import MQConsumer, GEC, read_gec_config, read_speller_config, Speller, MultiCorrector

parser = ArgumentParser(
    description="A neural grammatical error correction worker that processes incoming requests via "
                "RabbitMQ."
)
parser.add_argument('--gec-model-config', type=FileType('r'), default='models/GEC-synthetic-pretrain-ut-ft.yaml',
                    help="The GEC model config file.")
parser.add_argument('--spell-model-config', type=FileType('r'),
                    default='models/spell_etnc19_reference_corpus_6000000_web_2019_600000.yaml',
                    help="The Jamspell model config file.")
parser.add_argument('--log-config', type=FileType('r'), default='logging/logging.ini',
                    help="Path to log config file.")
parser.add_argument('--port', type=int, default='8000',
                    help="Port used for healthcheck probes.")

args = parser.parse_args()

app = FastAPI()
mq_thread = threading.Thread()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
async def startup():
    global mq_thread

    multi_corrector = MultiCorrector()

    if args.spell_model_config:
        speller_config = read_speller_config(args.spell_model_config.name)
        speller = Speller(speller_config)
        multi_corrector.add_corrector(speller)

    if args.gec_model_config:
        gec_config = read_gec_config(args.gec_model_config.name)
        gec = GEC(gec_config)
        multi_corrector.add_corrector(gec)

    consumer = MQConsumer(corrector=multi_corrector)

    mq_thread = threading.Thread(target=consumer.start)
    mq_thread.connected = False
    mq_thread.consume = True
    mq_thread.start()


@app.on_event("shutdown")
async def shutdown():
    global mq_thread
    mq_thread.consume = False


@app.get('/health/readiness')
@app.get('/health/startup')
async def health_check():
    # Returns 200 if models are loaded and connection to RabbitMQ is up
    global mq_thread
    if not mq_thread.is_alive() or not getattr(mq_thread, "connected"):
        raise HTTPException(500)
    return "OK"


@app.get('/health/liveness')
async def liveness():
    global mq_thread
    if not mq_thread.is_alive():
        raise HTTPException(500)
    return "OK"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_config=args.log_config.name)
