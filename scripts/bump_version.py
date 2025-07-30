#!/usr/bin/env python3
"""
Simple script to bump version numbers in pyproject.toml and __init__.py
"""

import re
import sys
from pathlib import Path


def update_pyproject_toml(version: str) -> None:
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)
    
    content = pyproject_path.read_text()
    
    # Update version line
    pattern = r'version = "([^"]+)"'
    replacement = f'version = "{version}"'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        pyproject_path.write_text(new_content)
        print(f"✅ Updated pyproject.toml version to {version}")
    else:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)


def update_init_py(version: str) -> None:
    """Update version in __init__.py"""
    init_path = Path("src/elastic_zeroentropy/__init__.py")
    
    if not init_path.exists():
        print("Error: __init__.py not found")
        sys.exit(1)
    
    content = init_path.read_text()
    
    # Update version line
    pattern = r'__version__ = "([^"]+)"'
    replacement = f'__version__ = "{version}"'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        init_path.write_text(new_content)
        print(f"✅ Updated __init__.py version to {version}")
    else:
        print("Error: Could not find __version__ in __init__.py")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <version>")
        print("Example: python scripts/bump_version.py 0.1.1")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print("Error: Version must be in format X.Y.Z (e.g., 0.1.1)")
        sys.exit(1)
    
    print(f"🔄 Bumping version to {version}...")
    
    try:
        update_pyproject_toml(version)
        update_init_py(version)
        print(f"✅ Successfully bumped version to {version}")
        print("\nNext steps:")
        print("1. git add pyproject.toml src/elastic_zeroentropy/__init__.py")
        print("2. git commit -m 'Bump version to {version}'")
        print("3. git tag v{version}")
        print("4. git push origin main")
        print("5. git push origin v{version}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 