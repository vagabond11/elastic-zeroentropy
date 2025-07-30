#!/usr/bin/env python3
"""
Deployment Health Check Script

This script checks the health of the elastic-zeroentropy deployment
and provides detailed status information.
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def check_package_build():
    """Check if the package can be built successfully."""
    print("🔨 Checking package build...")
    try:
        result = subprocess.run([sys.executable, "-m", "build"], 
                              capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        if result.returncode == 0:
            print("✅ Package builds successfully")
            return True
        else:
            print(f"❌ Package build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Build check failed: {e}")
        return False

def check_package_installation():
    """Check if the built package can be installed."""
    print("📦 Checking package installation...")
    try:
        # Find the wheel file
        dist_dir = Path(__file__).parent.parent / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))
        
        if not wheel_files:
            print("❌ No wheel files found in dist/")
            return False
        
        wheel_file = wheel_files[0]
        result = subprocess.run([sys.executable, "-m", "pip", "install", str(wheel_file)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Package installs successfully")
            return True
        else:
            print(f"❌ Package installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Installation check failed: {e}")
        return False

def check_pypi_availability():
    """Check if the package is available on PyPI."""
    print("🌐 Checking PyPI availability...")
    try:
        response = requests.get("https://pypi.org/pypi/elastic-zeroentropy/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['info']['version']
            print(f"✅ Package available on PyPI. Latest version: {latest_version}")
            return True
        else:
            print("⚠️ Package not found on PyPI")
            return False
    except Exception as e:
        print(f"❌ PyPI check failed: {e}")
        return False

def check_import_functionality():
    """Check if the package can be imported and basic functionality works."""
    print("🔍 Checking import functionality...")
    try:
        import elastic_zeroentropy
        print(f"✅ Package imports successfully. Version: {elastic_zeroentropy.__version__}")
        
        # Test basic imports
        from elastic_zeroentropy import RerankerConfig, SearchResponse, ElasticZeroEntropyReranker
        print("✅ Core classes import successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Functionality check failed: {e}")
        return False

def check_github_workflows():
    """Check if GitHub workflows are properly configured."""
    print("⚙️ Checking GitHub workflows...")
    workflow_dir = Path(__file__).parent.parent / ".github" / "workflows"
    
    required_workflows = ["publish.yml", "test.yml"]
    missing_workflows = []
    
    for workflow in required_workflows:
        if not (workflow_dir / workflow).exists():
            missing_workflows.append(workflow)
    
    if missing_workflows:
        print(f"❌ Missing workflows: {missing_workflows}")
        return False
    else:
        print("✅ All required workflows present")
        return True

def check_repository_settings():
    """Check repository configuration."""
    print("🔧 Checking repository settings...")
    
    # Check if we're in the right directory
    pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
    if not pyproject_file.exists():
        print("❌ pyproject.toml not found")
        return False
    
    # Check package name consistency
    try:
        import tomllib
        with open(pyproject_file, 'rb') as f:
            data = tomllib.load(f)
            package_name = data['project']['name']
            if package_name == "elastic-zeroentropy":
                print("✅ Package name is correct")
                return True
            else:
                print(f"❌ Package name mismatch: {package_name}")
                return False
    except Exception as e:
        print(f"❌ Could not read pyproject.toml: {e}")
        return False

def main():
    """Run all health checks."""
    print("🏥 Elastic-ZeroEntropy Deployment Health Check")
    print("=" * 50)
    
    checks = [
        ("Package Build", check_package_build),
        ("Package Installation", check_package_installation),
        ("PyPI Availability", check_pypi_availability),
        ("Import Functionality", check_import_functionality),
        ("GitHub Workflows", check_github_workflows),
        ("Repository Settings", check_repository_settings),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Deployment is healthy.")
        return 0
    else:
        print("⚠️ Some checks failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 