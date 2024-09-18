# standard imports
from yaml import safe_load
from pathlib import Path
import subprocess
import shutil
from loguru import logger

# custom imports

# typing imports
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class VoiceModelConfig(BaseModel):
    model_path: str = Field(..., description="Path to the voice model")
    channels: int = Field(default=1, description="Number of channels")
    sample_rate: int = Field(default=16000, description="Sample rate")
    chunk_size: int = Field(default=4096, description="Chunk size")
    frames_per_buffer: int = Field(default=8192, description="Frames per buffer")
    model_type: str = Field(default="vosk", description="Model type")

class LLMConfig(BaseModel):
    summary_model: str = Field(..., description="LLM model to generate summary")
    review_model: str = Field(..., description="LLM model to generate review")
    request_timeout: float = Field(default=60.0, description="Request timeout")
    chunk_size: int = Field(default=512, description="Chunk size")
    chunk_overlap: int = Field(default=75, description="Chunk overlap")
    embed_model: str = Field(default="BAAI/bge-small-en-v1.5", description="Embedding model")
    prompt_template: Dict[str, str] = Field(..., description="Prompt template")
    resume_summary_prompt: str = Field(..., description="Prompt to generate resume summary")
    job_description_summary_prompt: str = Field(..., description="Prompt to generate job description summary")

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
    

def download_ollama_model(model: str):
    """
    Download an Ollama model if it doesn't exist.
    
    Args:
        model (str): Name of the model to download.
    """
    if not shutil.which("ollama"):
        logger.error("Ollama is not installed or not in PATH. Please install Ollama first.")
        return

    try:
        # Check if the model exists
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model not in result.stdout:
            logger.info(f"Downloading Ollama model: {model}")
            subprocess.run(["ollama", "pull", model], check=True)
            logger.info(f"Successfully downloaded Ollama model: {model}")
        else:
            logger.info(f"Ollama model {model} already exists.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading Ollama model {model}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while processing Ollama model {model}: {e}")


