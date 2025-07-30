"""
Configuration management for elastic-zeroentropy library.

This module handles loading configuration from environment variables,
configuration files, and providing sensible defaults.
"""

import os
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from .exceptions import ConfigurationError

# Load environment variables from .env file if it exists
load_dotenv()


class ElasticZeroEntropyConfig(BaseSettings):
    """Configuration class for elastic-zeroentropy library."""

    # ZeroEntropy API Configuration
    zeroentropy_api_key: str = Field(
        ..., env="ZEROENTROPY_API_KEY", description="ZeroEntropy API key"
    )
    zeroentropy_base_url: str = Field(
        default="https://api.zeroentropy.dev/v1",
        env="ZEROENTROPY_BASE_URL",
        description="ZeroEntropy API base URL",
    )
    zeroentropy_model: str = Field(
        default="zerank-1",
        env="ZEROENTROPY_MODEL",
        description="Default ZeroEntropy model to use",
    )
    zeroentropy_timeout: float = Field(
        default=30.0,
        env="ZEROENTROPY_TIMEOUT",
        description="Request timeout for ZeroEntropy API calls in seconds",
    )
    zeroentropy_max_retries: int = Field(
        default=3,
        env="ZEROENTROPY_MAX_RETRIES",
        description="Maximum number of retry attempts for ZeroEntropy API calls",
        ge=0,
        le=10,
    )
    zeroentropy_retry_delay: float = Field(
        default=1.0,
        env="ZEROENTROPY_RETRY_DELAY",
        description="Base delay between retries in seconds",
        ge=0.1,
        le=60.0,
    )

    # Elasticsearch Configuration
    elasticsearch_url: str = Field(
        default="http://localhost:9200",
        env="ELASTICSEARCH_URL",
        description="Elasticsearch URL",
    )
    elasticsearch_username: Optional[str] = Field(
        default=None, env="ELASTICSEARCH_USERNAME", description="Elasticsearch username"
    )
    elasticsearch_password: Optional[str] = Field(
        default=None, env="ELASTICSEARCH_PASSWORD", description="Elasticsearch password"
    )
    elasticsearch_api_key: Optional[str] = Field(
        default=None, env="ELASTICSEARCH_API_KEY", description="Elasticsearch API key"
    )
    elasticsearch_verify_certs: bool = Field(
        default=True,
        env="ELASTICSEARCH_VERIFY_CERTS",
        description="Whether to verify SSL certificates for Elasticsearch",
    )
    elasticsearch_timeout: float = Field(
        default=30.0,
        env="ELASTICSEARCH_TIMEOUT",
        description="Request timeout for Elasticsearch operations in seconds",
    )
    elasticsearch_max_retries: int = Field(
        default=3,
        env="ELASTICSEARCH_MAX_RETRIES",
        description="Maximum number of retry attempts for Elasticsearch operations",
        ge=0,
        le=10,
    )

    # Default Search Configuration
    default_top_k_initial: int = Field(
        default=100,
        env="DEFAULT_TOP_K_INITIAL",
        description="Default number of documents to retrieve from Elasticsearch",
        ge=1,
        le=10000,
    )
    default_top_k_rerank: int = Field(
        default=20,
        env="DEFAULT_TOP_K_RERANK",
        description="Default number of documents to send for reranking",
        ge=1,
        le=1000,
    )
    default_top_k_final: int = Field(
        default=10,
        env="DEFAULT_TOP_K_FINAL",
        description="Default number of final results to return",
        ge=1,
        le=100,
    )
    default_combine_scores: bool = Field(
        default=True,
        env="DEFAULT_COMBINE_SCORES",
        description="Whether to combine Elasticsearch and reranking scores by default",
    )
    default_elasticsearch_weight: float = Field(
        default=0.3,
        env="DEFAULT_ELASTICSEARCH_WEIGHT",
        description="Default weight for Elasticsearch scores when combining",
        ge=0.0,
        le=1.0,
    )
    default_rerank_weight: float = Field(
        default=0.7,
        env="DEFAULT_RERANK_WEIGHT",
        description="Default weight for reranking scores when combining",
        ge=0.0,
        le=1.0,
    )

    # Logging and Debug Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    debug: bool = Field(default=False, env="DEBUG", description="Enable debug mode")
    enable_request_logging: bool = Field(
        default=False,
        env="ENABLE_REQUEST_LOGGING",
        description="Enable detailed request/response logging",
    )

    # Performance Configuration
    max_concurrent_requests: int = Field(
        default=10,
        env="MAX_CONCURRENT_REQUESTS",
        description="Maximum number of concurrent API requests",
        ge=1,
        le=100,
    )
    connection_pool_size: int = Field(
        default=20,
        env="CONNECTION_POOL_SIZE",
        description="HTTP connection pool size",
        ge=1,
        le=100,
    )

    # Rate Limiting Configuration
    enable_rate_limiting: bool = Field(
        default=True,
        env="ENABLE_RATE_LIMITING",
        description="Enable client-side rate limiting",
    )
    requests_per_minute: int = Field(
        default=1000,
        env="REQUESTS_PER_MINUTE",
        description="Maximum requests per minute when rate limiting is enabled",
        ge=1,
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "validate_assignment": True,
    }

    @field_validator("zeroentropy_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v.strip():
            raise ConfigurationError(
                "ZeroEntropy API key is required. Set ZEROENTROPY_API_KEY environment variable."
            )
        return v.strip()

    @field_validator("zeroentropy_base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ConfigurationError(
                f"Invalid ZeroEntropy base URL: {v}. Must start with http:// or https://"
            )
        return v.rstrip("/")

    @field_validator("elasticsearch_url")
    @classmethod
    def validate_elasticsearch_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ConfigurationError(
                f"Invalid Elasticsearch URL: {v}. Must start with http:// or https://"
            )
        return v.rstrip("/")

    @field_validator("default_rerank_weight")
    @classmethod
    def validate_combined_weights(cls, v: float, info) -> float:
        es_weight = info.data.get("default_elasticsearch_weight", 0.0)
        total = es_weight + v
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            raise ConfigurationError(
                f"Elasticsearch weight ({es_weight}) and rerank weight ({v}) must sum to 1.0"
            )
        return v

    @field_validator("default_top_k_rerank")
    @classmethod
    def validate_top_k_rerank(cls, v: int, info) -> int:
        initial = info.data.get("default_top_k_initial", 100)
        if v > initial:
            raise ConfigurationError(
                f"default_top_k_rerank ({v}) cannot exceed default_top_k_initial ({initial})"
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ConfigurationError(
                f"Invalid log level: {v}. Must be one of {valid_levels}"
            )
        return v.upper()

    def get_elasticsearch_auth(self) -> Optional[Dict[str, Any]]:
        """Get Elasticsearch authentication configuration."""
        if self.elasticsearch_api_key:
            return {"api_key": self.elasticsearch_api_key}
        elif self.elasticsearch_username and self.elasticsearch_password:
            return {
                "basic_auth": (self.elasticsearch_username, self.elasticsearch_password)
            }
        return None

    def get_zeroentropy_headers(self) -> Dict[str, str]:
        """Get headers for ZeroEntropy API requests."""
        return {
            "Authorization": f"Bearer {self.zeroentropy_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "elastic-zeroentropy/0.1.0",
        }

    def get_reranker_config_dict(self) -> Dict[str, Any]:
        """Get default reranker configuration as dictionary."""
        return {
            "top_k_initial": self.default_top_k_initial,
            "top_k_rerank": self.default_top_k_rerank,
            "top_k_final": self.default_top_k_final,
            "model": self.zeroentropy_model,
            "combine_scores": self.default_combine_scores,
            "score_weights": {
                "elasticsearch": self.default_elasticsearch_weight,
                "rerank": self.default_rerank_weight,
            },
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ElasticZeroEntropyConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)

    @classmethod
    def from_env_file(cls, env_file: str) -> "ElasticZeroEntropyConfig":
        """Create configuration from specific environment file."""
        if not os.path.exists(env_file):
            raise ConfigurationError(f"Environment file not found: {env_file}")

        load_dotenv(env_file)
        return cls()

    def validate_configuration(self) -> None:
        """Validate the complete configuration and raise errors if invalid."""
        errors = []

        # Check required fields
        if not self.zeroentropy_api_key:
            errors.append("ZeroEntropy API key is required")

        # Validate URL formats
        try:
            from urllib.parse import urlparse

            parsed_ze_url = urlparse(self.zeroentropy_base_url)
            if not parsed_ze_url.scheme or not parsed_ze_url.netloc:
                errors.append(
                    f"Invalid ZeroEntropy base URL: {self.zeroentropy_base_url}"
                )

            parsed_es_url = urlparse(self.elasticsearch_url)
            if not parsed_es_url.scheme or not parsed_es_url.netloc:
                errors.append(f"Invalid Elasticsearch URL: {self.elasticsearch_url}")

        except Exception as e:
            errors.append(f"URL validation error: {e}")

        # Validate consistency of top_k values
        if self.default_top_k_rerank > self.default_top_k_initial:
            errors.append("default_top_k_rerank cannot exceed default_top_k_initial")

        if self.default_top_k_final > self.default_top_k_rerank:
            errors.append("default_top_k_final cannot exceed default_top_k_rerank")

        if errors:
            raise ConfigurationError(
                "Configuration validation failed", details={"errors": errors}
            )


def load_config(
    config_dict: Optional[Dict[str, Any]] = None, env_file: Optional[str] = None
) -> ElasticZeroEntropyConfig:
    """
    Load configuration from various sources.

    Args:
        config_dict: Dictionary of configuration values
        env_file: Path to environment file

    Returns:
        Loaded and validated configuration

    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        if env_file:
            config = ElasticZeroEntropyConfig.from_env_file(env_file)
        elif config_dict:
            config = ElasticZeroEntropyConfig.from_dict(config_dict)
        else:
            config = ElasticZeroEntropyConfig()

        config.validate_configuration()
        return config

    except Exception as e:
        if isinstance(e, ConfigurationError):
            raise
        raise ConfigurationError(f"Failed to load configuration: {e}")


# Global configuration instance - can be overridden
_global_config: Optional[ElasticZeroEntropyConfig] = None


def get_config() -> ElasticZeroEntropyConfig:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config


def set_config(config: ElasticZeroEntropyConfig) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config
