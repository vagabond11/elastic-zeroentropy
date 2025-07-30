# Publishing Guide for elastic-zeroentropy

This guide covers how to publish the `elastic-zeroentropy` library to PyPI and manage releases.

## 🚀 Quick Release Process

### Automated Release (Recommended)

1. **Go to GitHub Actions**: https://github.com/vagabond11/elastic-zeroentropy/actions
2. **Select "Release" workflow**
3. **Click "Run workflow"**
4. **Fill in the form**:
   - **Version**: e.g., `0.1.1`
   - **Release Type**: `patch`, `minor`, or `major`
   - **Publish to PyPI**: ✅ (checked by default)
5. **Click "Run workflow"**

This will automatically:
- ✅ Build the package
- ✅ Create a GitHub release
- ✅ Upload release assets
- ✅ Publish to PyPI (if enabled)

### Manual Release

```bash
# 1. Update version in pyproject.toml
# 2. Update version in src/elastic_zeroentropy/__init__.py
# 3. Update CHANGELOG.md
# 4. Commit changes
git add .
git commit -m "Bump version to 0.1.1"
git push origin main

# 5. Create and push tag
git tag v0.1.1
git push origin v0.1.1

# 6. Create GitHub release manually
# Go to: https://github.com/vagabond11/elastic-zeroentropy/releases/new
```

## 📋 Pre-Publishing Checklist

### 1. Update Version
Update the version in `pyproject.toml`:
```toml
version = "0.1.1"  # Change to new version
```

And in `src/elastic_zeroentropy/__init__.py`:
```python
__version__ = "0.1.1"
```

### 2. Update Changelog
Add release notes to `CHANGELOG.md`:
```markdown
## [0.1.1] - 2024-01-XX

### Added
- New feature X
- New feature Y

### Changed
- Improved performance
- Updated dependencies

### Fixed
- Bug fix A
- Bug fix B
```

### 3. Run Quality Checks
```bash
# Run all tests
make test

# Run linting
make lint

# Run security checks
make security

# Check version consistency
make check-version
```

### 4. Test Build Locally
```bash
# Clean previous builds
make clean

# Build package
make build

# Check package
twine check dist/*

# Test installation
pip install dist/elastic_zeroentropy-0.1.1-py3-none-any.whl
```

## 🔧 GitHub Secrets Required

### For PyPI Publishing
- **`PYPI_API_TOKEN`**: Your PyPI API token
  - Get from: https://pypi.org/manage/account/token/
  - Format: `pypi-AgEIcHlwaS5vcmcC...`

### For Testing (Optional)
- **`ZEROENTROPY_API_KEY`**: For running tests with real API
- **`CODECOV_TOKEN`**: For coverage reporting

## 🛠️ Manual Publishing Steps

If you need to publish manually:

### 1. Build Package
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build source and wheel distributions
python -m build
```

### 2. Check Package
```bash
# Validate distribution
twine check dist/*
```

### 3. Test on TestPyPI (Recommended)
```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ elastic-zeroentropy
```

### 4. Publish to PyPI
```bash
# Upload to PyPI
twine upload dist/*
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Authentication Error**
```
HTTPError: 403 Forbidden from https://pypi.org/legacy/
```
**Solution**: Check your `PYPI_API_TOKEN` secret in GitHub repository settings.

#### 2. **Version Already Exists**
```
HTTPError: 400 Bad Request from https://pypi.org/legacy/
File already exists.
```
**Solution**: Increment version number in `pyproject.toml` and `__init__.py`.

#### 3. **Build Errors**
```
ModuleNotFoundError: No module named 'build'
```
**Solution**: Install build tools:
```bash
pip install build twine
```

#### 4. **Test Failures**
```
pytest: command not found
```
**Solution**: Install development dependencies:
```bash
pip install -e ".[dev]"
```

#### 5. **Linting Errors**
```
flake8: command not found
```
**Solution**: Install linting tools:
```bash
pip install flake8 black isort mypy bandit
```

### Workflow Issues

#### 1. **CI/CD Pipeline Failing**
- Check GitHub Actions logs: https://github.com/vagabond11/elastic-zeroentropy/actions
- Ensure all secrets are configured
- Check Python version compatibility

#### 2. **Release Workflow Not Triggering**
- Ensure you're on the `main` branch
- Check workflow permissions in repository settings
- Verify GitHub token permissions

#### 3. **Publish Job Skipped**
- Ensure `publish_to_pypi` is set to `true`
- Check that `PYPI_API_TOKEN` secret exists
- Verify release was created successfully

## 📊 Post-Publishing Verification

### 1. Verify PyPI Installation
```bash
# Test installation from PyPI
pip install elastic-zeroentropy

# Test basic functionality
python -c "import elastic_zeroentropy; print('Installation successful!')"
```

### 2. Verify GitHub Release
- Check: https://github.com/vagabond11/elastic-zeroentropy/releases
- Ensure assets are uploaded
- Verify release notes are complete

### 3. Update Documentation
- Update any version-specific documentation
- Update badges if needed
- Update examples if API changed

## 🎯 Best Practices

### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update both `pyproject.toml` and `__init__.py`
- Keep `CHANGELOG.md` up to date

### Release Process
- Always test on TestPyPI first
- Use automated workflows when possible
- Include comprehensive release notes
- Tag releases with `v` prefix (e.g., `v0.1.1`)

### Quality Assurance
- Run full test suite before release
- Ensure all linting passes
- Check security vulnerabilities
- Verify package builds correctly

## 🔗 Useful Links

- **PyPI**: https://pypi.org/project/elastic-zeroentropy/
- **TestPyPI**: https://test.pypi.org/project/elastic-zeroentropy/
- **GitHub Releases**: https://github.com/vagabond11/elastic-zeroentropy/releases
- **GitHub Actions**: https://github.com/vagabond11/elastic-zeroentropy/actions
- **PyPI Token Management**: https://pypi.org/manage/account/token/

## 📞 Support

For issues with publishing:
- Check PyPI status: https://status.python.org/
- Review PyPI documentation: https://packaging.python.org/
- Check GitHub Actions documentation: https://docs.github.com/en/actions 