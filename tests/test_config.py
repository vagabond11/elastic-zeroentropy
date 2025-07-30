"""Tests for configuration module."""

import os
from unittest.mock import mock_open, patch

import pytest
from pydantic import ValidationError

from elastic_zeroentropy.config import (
    ElasticZeroEntropyConfig,
    get_config,
    load_config,
    set_config,
)
from elastic_zeroentropy.exceptions import ConfigurationError


class TestElasticZeroEntropyConfig:
    """Test configuration class."""

    def test_default_configuration(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {"ZEROENTROPY_API_KEY": "test-key"}):
            config = ElasticZeroEntropyConfig()

            assert config.zeroentropy_api_key == "test-key"
            assert config.zeroentropy_base_url == "https://api.zeroentropy.dev/v1"
            assert config.zeroentropy_model == "zerank-1"
            assert config.elasticsearch_url == "http://localhost:9200"
            assert config.default_top_k_initial == 100
            assert config.default_top_k_rerank == 20
            assert config.default_top_k_final == 10

    def test_configuration_from_env(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "ZEROENTROPY_API_KEY": "custom-key",
            "ZEROENTROPY_BASE_URL": "https://custom.api.com/v1",
            "ZEROENTROPY_MODEL": "zerank-1-small",
            "ELASTICSEARCH_URL": "https://es.example.com:9200",
            "DEFAULT_TOP_K_INITIAL": "50",
            "DEFAULT_TOP_K_RERANK": "15",
            "DEFAULT_TOP_K_FINAL": "5",
        }

        with patch.dict(os.environ, env_vars):
            config = ElasticZeroEntropyConfig()

            assert config.zeroentropy_api_key == "custom-key"
            assert config.zeroentropy_base_url == "https://custom.api.com/v1"
            assert config.zeroentropy_model == "zerank-1-small"
            assert config.elasticsearch_url == "https://es.example.com:9200"
            assert config.default_top_k_initial == 50
            assert config.default_top_k_rerank == 15
            assert config.default_top_k_final == 5

    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises validation error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError):
                ElasticZeroEntropyConfig()

    def test_empty_api_key_raises_error(self):
        """Test that empty API key raises configuration error."""
        with patch.dict(os.environ, {"ZEROENTROPY_API_KEY": ""}):
            with pytest.raises(ConfigurationError):
                ElasticZeroEntropyConfig()

    def test_invalid_url_raises_error(self):
        """Test that invalid URLs raise configuration errors."""
        with patch.dict(
            os.environ,
            {"ZEROENTROPY_API_KEY": "test-key", "ZEROENTROPY_BASE_URL": "invalid-url"},
        ):
            with pytest.raises(ConfigurationError):
                ElasticZeroEntropyConfig()

    def test_invalid_weights_raise_error(self):
        """Test that weights not summing to 1.0 raise error."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "test-key",
                "DEFAULT_ELASTICSEARCH_WEIGHT": "0.5",
                "DEFAULT_RERANK_WEIGHT": "0.6",  # Sum = 1.1
            },
        ):
            with pytest.raises(ConfigurationError):
                ElasticZeroEntropyConfig()

    def test_get_elasticsearch_auth_with_api_key(self):
        """Test Elasticsearch auth configuration with API key."""
        with patch.dict(
            os.environ,
            {"ZEROENTROPY_API_KEY": "test-key", "ELASTICSEARCH_API_KEY": "es-api-key"},
        ):
            config = ElasticZeroEntropyConfig()
            auth = config.get_elasticsearch_auth()

            assert auth == {"api_key": "es-api-key"}

    def test_get_elasticsearch_auth_with_basic_auth(self):
        """Test Elasticsearch auth configuration with basic auth."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "test-key",
                "ELASTICSEARCH_USERNAME": "user",
                "ELASTICSEARCH_PASSWORD": "pass",
            },
        ):
            config = ElasticZeroEntropyConfig()
            auth = config.get_elasticsearch_auth()

            assert auth == {"basic_auth": ("user", "pass")}

    def test_get_elasticsearch_auth_no_auth(self):
        """Test Elasticsearch auth configuration with no auth."""
        with patch.dict(os.environ, {"ZEROENTROPY_API_KEY": "test-key"}):
            config = ElasticZeroEntropyConfig()
            auth = config.get_elasticsearch_auth()

            assert auth is None

    def test_get_zeroentropy_headers(self):
        """Test ZeroEntropy headers generation."""
        with patch.dict(os.environ, {"ZEROENTROPY_API_KEY": "test-key"}):
            config = ElasticZeroEntropyConfig()
            headers = config.get_zeroentropy_headers()

            expected_headers = {
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json",
                "User-Agent": "elastic-zeroentropy/0.1.0",
            }

            assert headers == expected_headers

    def test_get_reranker_config_dict(self):
        """Test reranker configuration dictionary generation."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "test-key",
                "DEFAULT_TOP_K_INITIAL": "50",
                "DEFAULT_TOP_K_RERANK": "15",
                "DEFAULT_TOP_K_FINAL": "5",
            },
        ):
            config = ElasticZeroEntropyConfig()
            reranker_config = config.get_reranker_config_dict()

            expected_config = {
                "top_k_initial": 50,
                "top_k_rerank": 15,
                "top_k_final": 5,
                "model": "zerank-1",
                "combine_scores": True,
                "score_weights": {"elasticsearch": 0.3, "rerank": 0.7},
            }

            assert reranker_config == expected_config

    def test_validate_configuration_success(self):
        """Test successful configuration validation."""
        with patch.dict(os.environ, {"ZEROENTROPY_API_KEY": "test-key"}):
            config = ElasticZeroEntropyConfig()
            # Should not raise an exception
            config.validate_configuration()

    def test_validate_configuration_invalid_top_k(self):
        """Test configuration validation with invalid top_k values."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "test-key",
                "DEFAULT_TOP_K_INITIAL": "10",
                "DEFAULT_TOP_K_RERANK": "20",  # Greater than initial
            },
        ):
            with pytest.raises(ConfigurationError):
                ElasticZeroEntropyConfig()


class TestConfigurationLoading:
    """Test configuration loading functions."""

    def test_load_config_default(self):
        """Test loading default configuration."""
        with patch.dict(os.environ, {"ZEROENTROPY_API_KEY": "test-key"}):
            config = load_config()
            assert isinstance(config, ElasticZeroEntropyConfig)
            assert config.zeroentropy_api_key == "test-key"

    def test_load_config_from_dict(self):
        """Test loading configuration from dictionary."""
        config_dict = {
            "zeroentropy_api_key": "dict-key",
            "zeroentropy_model": "custom-model",
            "default_top_k_final": 15,
        }

        config = load_config(config_dict=config_dict)
        assert config.zeroentropy_api_key == "dict-key"
        assert config.zeroentropy_model == "custom-model"
        assert config.default_top_k_final == 15

    def test_load_config_from_env_file(self):
        """Test loading configuration from environment file."""
        env_content = """
ZEROENTROPY_API_KEY=file-key
ZEROENTROPY_MODEL=file-model
DEFAULT_TOP_K_FINAL=8
"""

        with patch("builtins.open", mock_open(read_data=env_content)):
            with patch("os.path.exists", return_value=True):
                with patch("elastic_zeroentropy.config.load_dotenv"):
                    with patch.dict(
                        os.environ,
                        {
                            "ZEROENTROPY_API_KEY": "file-key",
                            "ZEROENTROPY_MODEL": "file-model",
                            "DEFAULT_TOP_K_FINAL": "8",
                        },
                    ):
                        config = load_config(env_file=".env.test")
                        assert config.zeroentropy_api_key == "file-key"
                        assert config.zeroentropy_model == "file-model"
                        assert config.default_top_k_final == 8

    def test_load_config_env_file_not_found(self):
        """Test loading configuration from non-existent file."""
        with pytest.raises(ConfigurationError):
            load_config(env_file="non-existent.env")

    def test_global_config_management(self):
        """Test global configuration management."""
        with patch.dict(os.environ, {"ZEROENTROPY_API_KEY": "test-key"}):
            # Test get_config creates instance
            config1 = get_config()
            assert isinstance(config1, ElasticZeroEntropyConfig)

            # Test get_config returns same instance
            config2 = get_config()
            assert config1 is config2

            # Test set_config changes global instance
            new_config = ElasticZeroEntropyConfig()
            set_config(new_config)
            config3 = get_config()
            assert config3 is new_config
            assert config3 is not config1


class TestConfigurationFromDict:
    """Test configuration creation from dictionary."""

    def test_from_dict_success(self):
        """Test successful configuration creation from dictionary."""
        config_dict = {
            "zeroentropy_api_key": "dict-key",
            "elasticsearch_url": "http://localhost:9200",
            "default_top_k_final": 5,
        }

        config = ElasticZeroEntropyConfig.from_dict(config_dict)
        assert config.zeroentropy_api_key == "dict-key"
        assert config.elasticsearch_url == "http://localhost:9200"
        assert config.default_top_k_final == 5

    def test_from_dict_validation_error(self):
        """Test configuration creation with validation errors."""
        config_dict = {
            "zeroentropy_api_key": "",  # Empty key should fail
            "elasticsearch_url": "invalid-url",
        }

        with pytest.raises(ConfigurationError):
            ElasticZeroEntropyConfig.from_dict(config_dict)


class TestConfigurationEdgeCases:
    """Test edge cases in configuration."""

    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case insensitive."""
        with patch.dict(
            os.environ,
            {
                "zeroentropy_api_key": "test-key",  # lowercase
                "ELASTICSEARCH_URL": "http://es:9200",  # uppercase
            },
        ):
            config = ElasticZeroEntropyConfig()
            assert config.zeroentropy_api_key == "test-key"
            assert config.elasticsearch_url == "http://es:9200"

    def test_whitespace_stripping(self):
        """Test that whitespace is stripped from string values."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "  test-key  ",
                "ZEROENTROPY_BASE_URL": "  https://api.example.com/v1  ",
            },
        ):
            config = ElasticZeroEntropyConfig()
            assert config.zeroentropy_api_key == "test-key"
            assert config.zeroentropy_base_url == "https://api.example.com/v1"

    def test_boolean_parsing(self):
        """Test boolean value parsing from environment."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "test-key",
                "DEBUG": "true",
                "ENABLE_RATE_LIMITING": "false",
                "ELASTICSEARCH_VERIFY_CERTS": "1",
            },
        ):
            config = ElasticZeroEntropyConfig()
            assert config.debug is True
            assert config.enable_rate_limiting is False
            assert config.elasticsearch_verify_certs is True

    def test_numeric_validation(self):
        """Test numeric value validation."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "test-key",
                "ZEROENTROPY_MAX_RETRIES": "15",  # Should be clamped to max 10
            },
        ):
            with pytest.raises(ValidationError):
                ElasticZeroEntropyConfig()

    def test_url_normalization(self):
        """Test URL normalization (trailing slash removal)."""
        with patch.dict(
            os.environ,
            {
                "ZEROENTROPY_API_KEY": "test-key",
                "ZEROENTROPY_BASE_URL": "https://api.example.com/v1/",
                "ELASTICSEARCH_URL": "http://localhost:9200/",
            },
        ):
            config = ElasticZeroEntropyConfig()
            assert config.zeroentropy_base_url == "https://api.example.com/v1"
            assert config.elasticsearch_url == "http://localhost:9200"
