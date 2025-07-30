# Contributing to elastic-zeroentropy

Thank you for your interest in contributing to elastic-zeroentropy! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues**: Search the [GitHub issues](https://github.com/vagabond11/elastic-zeroentropy/issues) to see if the bug has already been reported.
2. **Create a new issue**: If it's a new bug, create an issue with:
   - Clear title describing the problem
   - Detailed description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

### Suggesting Features

1. **Check existing issues**: Search for similar feature requests.
2. **Create a feature request**: Use the feature request template and include:
   - Clear description of the feature
   - Use cases and benefits
   - Implementation suggestions (if any)

### Submitting Code Changes

1. **Fork the repository**: Click the "Fork" button on GitHub.
2. **Create a feature branch**: Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**: Follow the coding standards below.
4. **Add tests**: Include tests for new functionality.
5. **Update documentation**: Update relevant documentation.
6. **Commit your changes**: Use clear, descriptive commit messages.
7. **Push to your fork**: Push your branch to your fork.
8. **Create a pull request**: Submit a PR with a clear description.

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vagabond11/elastic-zeroentropy.git
cd elastic-zeroentropy
   ```

2. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=elastic_zeroentropy --cov-report=html

# Run specific test file
pytest tests/test_reranker.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Run flake8 linting
flake8 src/ tests/

# Run mypy type checking
mypy src/
```

## 📝 Coding Standards

### Code Style

- **Black**: We use Black for code formatting. Run `black src/ tests/` before committing.
- **isort**: We use isort for import sorting. Run `isort src/ tests/` before committing.
- **flake8**: We use flake8 for linting. All code should pass flake8 checks.
- **mypy**: We use mypy for type checking. All code should pass mypy checks.

### Python Code Standards

- **Type hints**: Use type hints for all function parameters and return values.
- **Docstrings**: Use Google-style docstrings for all public functions and classes.
- **Error handling**: Use custom exceptions from `elastic_zeroentropy.exceptions`.
- **Async/await**: Use async/await for all I/O operations.
- **Logging**: Use the standard logging module with appropriate levels.

### Example Code Structure

```python
from typing import Optional, List
from elastic_zeroentropy.exceptions import ValidationError

def example_function(param: str, optional_param: Optional[int] = None) -> List[str]:
    """
    Example function with proper documentation.
    
    Args:
        param: Required parameter description.
        optional_param: Optional parameter description.
        
    Returns:
        List of strings with results.
        
    Raises:
        ValidationError: If param is empty or invalid.
    """
    if not param:
        raise ValidationError("param cannot be empty", field="param")
    
    # Implementation here
    return ["result"]
```

### Test Standards

- **Test coverage**: Aim for >95% test coverage.
- **Test naming**: Use descriptive test names that explain what is being tested.
- **Test organization**: Group related tests in classes.
- **Mocking**: Use pytest-mock for mocking external dependencies.
- **Async tests**: Use `@pytest.mark.asyncio` for async test functions.

### Example Test Structure

```python
import pytest
from elastic_zeroentropy import ElasticZeroEntropyReranker

class TestExampleFeature:
    """Test example feature functionality."""
    
    @pytest.mark.asyncio
    async def test_feature_works_correctly(self, mock_config):
        """Test that the feature works as expected."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)
        
        # Test implementation
        result = await reranker.some_method("test")
        
        assert result is not None
        assert result.value == "expected"
    
    def test_feature_validation(self, mock_config):
        """Test that validation works correctly."""
        with pytest.raises(ValidationError, match="Invalid input"):
            # Test validation
            pass
```

## 📚 Documentation Standards

### Docstrings

- Use Google-style docstrings for all public APIs.
- Include type hints in docstrings.
- Provide clear examples for complex functions.

### README Updates

- Update README.md for new features or breaking changes.
- Include usage examples for new functionality.
- Update installation instructions if dependencies change.

### API Documentation

- Document all public classes and methods.
- Include parameter descriptions and return values.
- Provide usage examples for complex APIs.

## 🔄 Pull Request Process

### Before Submitting

1. **Run tests**: Ensure all tests pass locally.
2. **Check code quality**: Run black, isort, flake8, and mypy.
3. **Update documentation**: Update relevant documentation.
4. **Test installation**: Test that the package installs correctly.

### Pull Request Guidelines

1. **Clear title**: Use a clear, descriptive title.
2. **Detailed description**: Explain what the PR does and why.
3. **Link issues**: Link any related issues.
4. **Include tests**: Include tests for new functionality.
5. **Update docs**: Update documentation as needed.

### PR Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

## 🚀 Release Process

### Version Management

- Follow [Semantic Versioning](https://semver.org/).
- Update version in `pyproject.toml` and `src/elastic_zeroentropy/__init__.py`.
- Update `CHANGELOG.md` with release notes.

### Release Steps

1. **Update version**: Update version numbers in relevant files.
2. **Update changelog**: Add release notes to `CHANGELOG.md`.
3. **Create release**: Create a GitHub release with the new version tag.
4. **Automated publishing**: The GitHub Action will automatically publish to PyPI.

## 🆘 Getting Help

- **GitHub Issues**: Use GitHub issues for bug reports and feature requests.
- **Discussions**: Use GitHub Discussions for questions and general discussion.
- **Documentation**: Check the README and docstrings for usage information.

## 📄 License

By contributing to elastic-zeroentropy, you agree that your contributions will be licensed under the MIT License.

## 🙏 Acknowledgments

Thank you for contributing to elastic-zeroentropy! Your contributions help make this project better for everyone. 