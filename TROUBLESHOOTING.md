# Troubleshooting Guide

This guide helps you resolve common issues with CI/CD workflows, publishing, and GitHub Actions.

## 🔧 Workflow Issues

### 1. **Tests Failing**

#### **Issue**: `ModuleNotFoundError: No module named 'elastic_zeroentropy'`
**Solution**: 
```bash
# Install in development mode
pip install -e ".[dev]"
```

#### **Issue**: `ZEROENTROPY_API_KEY` not set
**Solution**: 
- Add `ZEROENTROPY_API_KEY` to GitHub repository secrets
- Or use fallback: `ZEROENTROPY_API_KEY: ${{ secrets.ZEROENTROPY_API_KEY || 'test-key' }}`

#### **Issue**: Pydantic deprecation warnings
**Solution**: These are expected with pydantic-settings. They don't affect functionality.

### 2. **Build Failing**

#### **Issue**: `build` command not found
**Solution**:
```bash
pip install build twine
```

#### **Issue**: Package validation fails
**Solution**:
```bash
# Check package
twine check dist/*

# Rebuild if needed
python -m build
```

### 3. **Publishing Failing**

#### **Issue**: `403 Forbidden` from PyPI
**Solution**:
- Check `PYPI_API_TOKEN` secret in GitHub repository settings
- Ensure token has upload permissions
- Verify token format: `pypi-AgEIcHlwaS5vcmcC...`

#### **Issue**: `400 Bad Request - File already exists`
**Solution**:
- Increment version in `pyproject.toml` and `__init__.py`
- Update version to next patch: `0.1.0` → `0.1.1`

#### **Issue**: Release workflow not triggering
**Solution**:
- Ensure you're on `main` branch
- Check workflow permissions in repository settings
- Verify GitHub token permissions

## 🚀 Publishing Process

### **Manual Publishing Steps**

1. **Update Version**:
   ```bash
   # Edit pyproject.toml
   version = "0.1.1"
   
   # Edit src/elastic_zeroentropy/__init__.py
   __version__ = "0.1.1"
   ```

2. **Build Package**:
   ```bash
   make clean
   make build
   ```

3. **Test Package**:
   ```bash
   twine check dist/*
   pip install dist/elastic_zeroentropy-*.whl
   ```

4. **Publish to PyPI**:
   ```bash
   twine upload dist/*
   ```

### **Automated Publishing**

1. **Go to GitHub Actions**: https://github.com/vagabond11/elastic-zeroentropy/actions
2. **Select "Release" workflow**
3. **Click "Run workflow"**
4. **Fill in version and options**
5. **Click "Run workflow"**

## 🔍 Common Error Messages

### **GitHub Actions Errors**

#### **"No module named 'build'"**
```yaml
# Add to workflow
- name: Install build dependencies
  run: |
    python -m pip install --upgrade pip
    pip install build twine
```

#### **"ZEROENTROPY_API_KEY not set"**
```yaml
# Use fallback in workflow
env:
  ZEROENTROPY_API_KEY: ${{ secrets.ZEROENTROPY_API_KEY || 'test-key' }}
```

#### **"Coverage upload failed"**
```yaml
# Add condition
if: matrix.coverage && secrets.CODECOV_TOKEN != ''
```

#### **"Publish job skipped"**
```yaml
# Add condition
if: github.event.inputs.publish_to_pypi == 'true' && secrets.PYPI_API_TOKEN != ''
```

### **PyPI Errors**

#### **"403 Forbidden"**
- Check API token in GitHub secrets
- Verify token permissions
- Test token locally: `twine upload --repository testpypi dist/*`

#### **"400 Bad Request - File already exists"**
- Increment version number
- Check PyPI for existing version
- Use unique version number

#### **"Authentication failed"**
- Verify token format
- Check token expiration
- Regenerate token if needed

## 🛠️ Debugging Steps

### **1. Check Workflow Logs**
- Go to GitHub Actions tab
- Click on failed workflow
- Check specific job logs
- Look for error messages

### **2. Test Locally**
```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build package
python -m build

# Check package
twine check dist/*

# Test installation
pip install dist/elastic_zeroentropy-*.whl
```

### **3. Verify Secrets**
- Go to repository Settings → Secrets and variables → Actions
- Check if required secrets exist:
  - `PYPI_API_TOKEN`
  - `ZEROENTROPY_API_KEY` (optional)
  - `CODECOV_TOKEN` (optional)

### **4. Check Package Configuration**
```bash
# Validate pyproject.toml
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Check version consistency
grep -r "0.1.0" pyproject.toml src/elastic_zeroentropy/__init__.py
```

## 📋 Pre-Publishing Checklist

- [ ] **Version updated** in `pyproject.toml` and `__init__.py`
- [ ] **Changelog updated** with release notes
- [ ] **Tests passing** locally and in CI
- [ ] **Package builds** successfully
- [ ] **Package validates** with `twine check`
- [ ] **GitHub secrets** configured
- [ ] **Documentation updated** if needed

## 🔗 Useful Commands

### **Local Testing**
```bash
# Run all tests
make test

# Run linting
make lint

# Build package
make build

# Check package
twine check dist/*

# Test installation
pip install dist/elastic_zeroentropy-*.whl
```

### **GitHub Actions Debugging**
```bash
# Check workflow syntax
yamllint .github/workflows/*.yml

# Test workflow locally (if possible)
act -j test
```

### **PyPI Testing**
```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ elastic-zeroentropy

# Then publish to PyPI
twine upload dist/*
```

## 📞 Getting Help

### **GitHub Issues**
- Create issue: https://github.com/vagabond11/elastic-zeroentropy/issues
- Include workflow logs and error messages
- Provide reproduction steps

### **PyPI Support**
- PyPI status: https://status.python.org/
- PyPI documentation: https://packaging.python.org/
- PyPI token management: https://pypi.org/manage/account/token/

### **GitHub Actions Support**
- GitHub Actions docs: https://docs.github.com/en/actions
- GitHub Actions status: https://www.githubstatus.com/

## 🎯 Quick Fixes

### **Most Common Issues**

1. **Missing API Token**: Add `PYPI_API_TOKEN` to GitHub secrets
2. **Version Conflict**: Increment version number
3. **Build Dependencies**: Install `build twine`
4. **Test Dependencies**: Install `-e ".[dev]"`
5. **Workflow Permissions**: Check repository settings

### **Emergency Publishing**
```bash
# If GitHub Actions fails, publish manually
git clone https://github.com/vagabond11/elastic-zeroentropy.git
cd elastic-zeroentropy
pip install build twine
python -m build
twine upload dist/*
``` 