# Simple Publishing Guide

This guide shows you the simplest way to publish the `elastic-zeroentropy` library.

## 🚀 Quick Publish (Recommended)

### Method 1: GitHub Actions (Easiest)

1. **Go to GitHub Actions**: https://github.com/vagabond11/elastic-zeroentropy/actions
2. **Select "Publish to PyPI" workflow**
3. **Click "Run workflow"**
4. **Enter version** (e.g., `0.1.1`)
5. **Click "Run workflow"**

This will automatically:
- ✅ Update version in all files
- ✅ Run tests
- ✅ Build package
- ✅ Create Git tag and release
- ✅ Publish to PyPI (if token is set)

### Method 2: Manual Release

```bash
# 1. Bump version
make bump-version VERSION=0.1.1

# 2. Commit changes
git add pyproject.toml src/elastic_zeroentropy/__init__.py
git commit -m "Bump version to 0.1.1"

# 3. Create tag
git tag v0.1.1

# 4. Push to GitHub
git push origin main
git push origin v0.1.1

# 5. Create GitHub release manually
# Go to: https://github.com/vagabond11/elastic-zeroentropy/releases/new
```

## 🔧 Setup Required

### GitHub Secrets
Add these to your repository settings:

1. **`PYPI_API_TOKEN`** (Required for publishing)
   - Get from: https://pypi.org/manage/account/token/
   - Format: `pypi-AgEIcHlwaS5vcmcC...`

2. **`ZEROENTROPY_API_KEY`** (Optional, for testing)
   - Only needed if you want to run real API tests

### How to Add Secrets
1. Go to: https://github.com/vagabond11/elastic-zeroentropy/settings/secrets/actions
2. Click "New repository secret"
3. Add the secrets above

## 📋 Workflows Available

### 1. **Test Workflow** (`.github/workflows/test.yml`)
- Runs on every push and PR
- Tests on Python 3.8-3.12
- Builds and validates package
- No publishing

### 2. **Publish Workflow** (`.github/workflows/publish.yml`)
- Manual trigger only
- Updates version automatically
- Creates Git tag and release
- Publishes to PyPI

### 3. **Release Workflow** (`.github/workflows/python-publish.yml`)
- Triggers on GitHub releases
- Publishes to PyPI
- No version management

## 🛠️ Local Commands

### Version Management
```bash
# Show current version
make version

# Check version consistency
make check-version

# Bump version
make bump-version VERSION=0.1.1

# Prepare release
make release VERSION=0.1.1
```

### Testing
```bash
# Run tests
make test

# Build package
make build

# Check package
twine check dist/*
```

### Publishing
```bash
# Publish to PyPI
make publish

# Publish to TestPyPI
make publish-test
```

## 🎯 Simple Process

### For a New Release:

1. **Choose your method**:
   - **GitHub Actions** (easiest): Use the "Publish to PyPI" workflow
   - **Manual**: Use `make release VERSION=0.1.1`

2. **Verify the release**:
   - Check PyPI: https://pypi.org/project/elastic-zeroentropy/
   - Test installation: `pip install elastic-zeroentropy`

3. **Update documentation** (if needed):
   - Update CHANGELOG.md
   - Update examples

## 🔍 Troubleshooting

### Common Issues

#### **"403 Forbidden" from PyPI**
- Check `PYPI_API_TOKEN` secret in GitHub settings
- Verify token has upload permissions

#### **"File already exists"**
- Increment version number
- Check PyPI for existing version

#### **Workflow not triggering**
- Ensure you're on `main` branch
- Check workflow permissions

#### **Tests failing**
- Check `ZEROENTROPY_API_KEY` secret
- Or use fallback: `test-key`

### Quick Fixes

```bash
# If GitHub Actions fails, publish manually
make bump-version VERSION=0.1.1
make build
make publish

# Check current version
make version

# Verify package
twine check dist/*
```

## 📞 Support

- **GitHub Issues**: https://github.com/vagabond11/elastic-zeroentropy/issues
- **PyPI Status**: https://status.python.org/
- **GitHub Actions**: https://docs.github.com/en/actions

## 🎉 Success Checklist

After publishing, verify:

- [ ] **PyPI**: Package appears on https://pypi.org/project/elastic-zeroentropy/
- [ ] **Installation**: `pip install elastic-zeroentropy` works
- [ ] **GitHub Release**: Release created with assets
- [ ] **Version**: Correct version in all files
- [ ] **Tests**: All tests pass locally and in CI

That's it! The publishing process is now simple and reliable. 🚀 