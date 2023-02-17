import yaml
from yaml.loader import SafeLoader

from pydantic import BaseSettings, BaseModel


class MQConfig(BaseSettings):
    """
    Imports MQ configuration from environment variables
    """
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    exchange: str = 'grammar'
    heartbeat: int = 60
    connection_name: str = 'Grammar worker'

    class Config:
        env_prefix = 'mq_'


class WorkerConfig(BaseSettings):
    """
    Imports general worker configuration from environment variables
    """
    max_input_length: int = 10000

    class Config:
        env_prefix = 'worker_'


class ModelConfig(BaseModel):
    language: str  # actual ISO input language code
    checkpoint: str = "models/checkpoint_best.pt"
    dict_dir: str = "models/dicts/"
    sentencepiece_dir: str = "models/sentencepiece/"
    sentencepiece_prefix: str = "sp-model"
    source_language: str = "et0"  # input language code in the model
    target_language: str = "et1"  # target language code in the model


def read_model_config(file_path: str) -> ModelConfig:
    with open(file_path, 'r', encoding='utf-8') as f:
        model_config = ModelConfig(**yaml.load(f, Loader=SafeLoader))

    return model_config


mq_config = MQConfig()
worker_config = WorkerConfig()
