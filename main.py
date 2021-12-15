import logging.config
from argparse import ArgumentParser, FileType

from gec_worker import MQConsumer, GEC, MQConfig, read_model_config


def parse_args():
    parser = ArgumentParser(
        description="A neural grammatical error correction worker that processes incoming translation requests via "
                    "RabbitMQ."
    )
    parser.add_argument('--model-config', type=FileType('r'), default='models/config.yaml',
                        help="The model config YAML file to load.")
    parser.add_argument('--log-config', type=FileType('r'), default='logging/logging.ini',
                        help="Path to log config file.")

    return parser.parse_args()


def main():
    args = parse_args()
    logging.config.fileConfig(args.log_config.name)
    model_config = read_model_config(args.model_config.name)
    mq_config = MQConfig()

    gec = GEC(model_config)
    consumer = MQConsumer(
        gec=gec,
        mq_config=mq_config
    )

    consumer.start()


if __name__ == "__main__":
    main()
