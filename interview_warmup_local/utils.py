# standard imports
from yaml import safe_load
from pathlib import Path

# custom imports

# typing imports
from typing import Any, Dict

# Pydantic import
from pydantic import BaseModel, Field


class VoiceModelConfig(BaseModel):
    model_path: str = Field(..., description="Path to the voice model")
    channels: int = Field(default=1, description="Number of channels")
    sample_rate: int = Field(default=16000, description="Sample rate")
    chunk_size: int = Field(default=4096, description="Chunk size")
    frames_per_buffer: int = Field(default=8192, description="Frames per buffer")
    model_type: str = Field(default="vosk", description="Model type")

class LLMConfig(BaseModel):
    model: str = Field(..., description="LLM model")
    request_timeout: float = Field(default=60.0, description="Request timeout")
    chunk_size: int = Field(default=512, description="Chunk size")
    chunk_overlap: int = Field(default=75, description="Chunk overlap")
    embed_model: str = Field(default="BAAI/bge-small-en-v1.5", description="Embedding model")
    prompt_template: Dict[str, str] = Field(..., description="Prompt template")

class ConfigModel(BaseModel):
    voice_model: VoiceModelConfig = Field(..., description="Voice model configuration")
    llm: LLMConfig = Field(..., description="LLM configuration")


def read_config(config_path: str) -> ConfigModel:
    """
    Read the YAML config file and return a Pydantic model instance.
    
    Args:
        config_path (str): Path to the YAML config file. Defaults to "config.yaml".
    
    Returns:
        ConfigModel: Pydantic model instance containing the config data.
    
    Raises:
        FileNotFoundError: If the config file is not found.
        ValueError: If the config file is invalid or missing required fields.
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with config_file.open("r") as f:
        config_data: Dict[str, Any] = safe_load(f)
    
    try:
        return ConfigModel(**config_data)
    except ValueError as e:
        raise ValueError(f"Invalid config file: {e}")


