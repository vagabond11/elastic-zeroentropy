# Publishing Guide for elastic-zeroentropy

This guide covers how to publish the `elastic-zeroentropy` library to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/
2. **TestPyPI Account**: Create an account at https://test.pypi.org/ (for testing)
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI
4. **Build Tools**: Install required build tools

```bash
pip install build twine
```

## Pre-Publishing Checklist

### 1. Update Version
Update the version in `pyproject.toml`:
```toml
version = "0.1.0"  # Change to new version
```

### 2. Update Changelog
Add release notes to `CHANGELOG.md` (create if it doesn't exist).

### 3. Run Tests
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=elastic_zeroentropy --cov-report=html

# Type checking
mypy src/

# Code formatting
black src/ tests/
isort src/ tests/
```

### 4. Update Documentation
- Ensure README.md is up to date
- Check all examples work
- Verify installation instructions

## Publishing Steps

### 1. Build Distribution
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build source and wheel distributions
python -m build
```

### 2. Test on TestPyPI (Recommended)
```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ elastic-zeroentropy
```

### 3. Publish to PyPI
```bash
# Upload to PyPI
twine upload dist/*
```

## Post-Publishing

### 1. Verify Installation
```bash
# Test installation from PyPI
pip install elastic-zeroentropy

# Test basic functionality
python -c "import elastic_zeroentropy; print('Installation successful!')"
```

### 2. Update GitHub Release
- Create a new release on GitHub
- Tag with version (e.g., `v0.1.0`)
- Upload distribution files
- Add release notes

### 3. Update Documentation
- Update any version-specific documentation
- Update badges if needed

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure your API tokens are correct
2. **Version Already Exists**: Increment version number
3. **Build Errors**: Check for syntax errors and missing dependencies
4. **Upload Errors**: Verify network connection and PyPI status

### Useful Commands

```bash
# Check distribution contents
tar -tzf dist/elastic-zeroentropy-0.1.0.tar.gz

# Validate distribution
twine check dist/*

# Test installation in clean environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install elastic-zeroentropy
```

## Version Management

### Semantic Versioning
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Update Checklist
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `__init__.py` if needed
- [ ] Update changelog
- [ ] Update any version-specific documentation
- [ ] Test with new version

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Dependencies**: Regularly update dependencies for security patches
3. **Vulnerabilities**: Run security scans on dependencies

## Automation (Optional)

Consider setting up GitHub Actions for automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build and publish
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        python -m build
        twine upload dist/*
```

## Support

For issues with publishing:
- Check PyPI status: https://status.python.org/
- Review PyPI documentation: https://packaging.python.org/
- Check GitHub issues for known problems 