import os
import logging
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class Config(BaseSettings):
    """Configuration settings for the RAG Log Search Application."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # Vector Store Configuration
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    top_k_results: int = Field(default=5, env="TOP_K_RESULTS")
    
    # LLM Configuration
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, v: int) -> int:
        """Validate chunk size is positive."""
        if v <= 0:
            raise ValueError("chunk_size must be positive")
        return v
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Validate chunk overlap is less than chunk size."""
        if v < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if hasattr(info, "data") and "chunk_size" in info.data:
            if v >= info.data["chunk_size"]:
                raise ValueError("chunk_overlap must be less than chunk_size")
        return v
    
    @field_validator("top_k_results")
    @classmethod
    def validate_top_k_results(cls, v: int) -> int:
        """Validate top_k_results is positive."""
        if v <= 0:
            raise ValueError("top_k_results must be positive")
        return v
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is between 0 and 2."""
        if not 0 <= v <= 2:
            raise ValueError("temperature must be between 0 and 2")
        return v


def get_config() -> Config:
    """Get the application configuration with error handling."""
    try:
        config = Config()
        if not config.openai_api_key:
            logger.warning("OPENAI_API_KEY not set. Application will not function properly.")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


# Global config instance
try:
    config = get_config()
except Exception as e:
    logger.error(f"Failed to initialize config: {e}")
    config = None
