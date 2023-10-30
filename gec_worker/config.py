from typing import Optional
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
    huggingface: Optional[str] = None

    def download(self):
        if self.huggingface is not None:
            from huggingface_hub import Repository
            Repository(clone_from=self.huggingface, local_dir=f"models/{self.huggingface}")
        else:
            raise ValueError("Model cannot be downloaded, no HuggingFace repository specified.")


class GECModelConfig(ModelConfig):
    huggingface: Optional[str] = None
    checkpoint: str = "checkpoint_best.pt"
    dict_dir: str = "dicts/"
    sentencepiece_dir: str = "sentencepiece/"
    sentencepiece_prefix: str = "sp-model"
    truecase_model: str = "tc-model.tc"
    source_language: str = "et0"  # input language code in the model
    target_language: str = "et1"  # target language code in the model
    task: str = "multilingual_translation"  # task the model is trained on multilingual_translation
    type: str = "nelb" # No Error Left Behind type model


class SpellModelConfig(ModelConfig):
    huggingface: str
    model_bin: str


def read_gec_config(file_path: str) -> GECModelConfig:
    with open(file_path, 'r', encoding='utf-8') as f:
        model_config = GECModelConfig(**yaml.load(f, Loader=SafeLoader))

    return model_config


def read_speller_config(file_path: str) -> SpellModelConfig:
    with open(file_path, 'r', encoding='utf-8') as f:
        model_config = SpellModelConfig(**yaml.load(f, Loader=SafeLoader))

    return model_config


mq_config = MQConfig()
worker_config = WorkerConfig()
