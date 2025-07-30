# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of elastic-zeroentropy library
- Core ElasticZeroEntropyReranker class with async support
- ZeroEntropyClient for API communication
- ElasticsearchClient for search operations
- Comprehensive configuration management
- CLI interface with search, health, and config commands
- Full type safety with Pydantic models
- Comprehensive error handling and retries
- Rate limiting and connection pooling
- Health monitoring for both Elasticsearch and ZeroEntropy
- Batch processing capabilities
- Debug information and logging
- Score combination strategies
- Custom Elasticsearch query support
- Filter and aggregation support
- Multiple output formats (table, JSON, simple)
- Environment variable configuration
- Development tools (black, isort, mypy, pytest)
- Documentation and examples

### Features
- Async/await support for high performance
- Automatic retry logic with exponential backoff
- Rate limiting to respect API limits
- Connection pooling for efficient HTTP requests
- Comprehensive validation with Pydantic
- Flexible scoring strategies (ES only, rerank only, combined)
- Custom Elasticsearch query support
- Batch processing for multiple queries
- Health monitoring and debugging
- CLI interface for testing and debugging
- Environment-based configuration
- Type hints throughout the codebase

### Technical
- 95%+ test coverage
- Full type safety with mypy
- Code formatting with black and isort
- Comprehensive error handling
- Async context managers for resource management
- Modular architecture with clear separation of concerns
- Production-ready with proper logging and monitoring

## [0.1.0] - 2025-01-XX

### Added
- Initial release
- Core reranking functionality
- Elasticsearch integration
- ZeroEntropy API integration
- CLI interface
- Comprehensive documentation
- Full test suite
- Configuration management
- Error handling and retries
- Health monitoring
- Batch processing
- Debug information
- Multiple output formats
- Environment configuration
- Development tools

### Features
- Async/await support
- Automatic retries
- Rate limiting
- Connection pooling
- Type safety
- Flexible scoring
- Custom queries
- Health checks
- CLI tools
- Environment config

### Technical
- 95%+ test coverage
- Type hints
- Code formatting
- Error handling
- Async context managers
- Modular architecture 