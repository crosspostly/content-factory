#!/usr/bin/env python3
"""
Environment checker for CI/CD pipelines.
Run with: python -m core.utils.environment_checker
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_system_deps():
    """Check for required system dependencies."""
    print("\n🔍 Checking system dependencies...")
    
    deps = {
        'ffmpeg': 'ffmpeg -version',
        'python': 'python --version',
    }
    
    missing = []
    for dep, cmd in deps.items():
        if not shutil.which(dep):
            missing.append(dep)
        else:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    first_line = result.stdout.strip().split('\n')[0]
                    print(f"  ✅ {dep}: {first_line}")
                else:
                    missing.append(dep)
            except Exception as e:
                print(f"  ⚠️  {dep}: {e}")
    
    if missing:
        print(f"  ❌ Missing: {', '.join(missing)}")
        return False
    return True


def check_python_packages():
    """Check for required Python packages."""
    print("\n🔍 Checking Python packages...")
    
    try:
        import google.generativeai
        print(f"  ✅ google-generativeai: installed")
    except ImportError:
        print(f"  ⚠️  google-generativeai: not installed (optional)")
    
    try:
        import pytest
        print(f"  ✅ pytest: installed")
    except ImportError:
        print(f"  ⚠️  pytest: not installed (required for tests)")
    
    return True


def check_env_vars():
    """Check for required environment variables."""
    print("\n🔍 Checking environment variables...")
    
    optional_vars = ['GOOGLE_AI_API_KEY', 'PIXABAY_API_KEY']
    
    for var in optional_vars:
        if os.getenv(var):
            value = os.getenv(var)
            masked = value[:4] + '*' * max(0, len(value) - 8) + (value[-4:] if len(value) > 4 else '')
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ⚠️  {var}: not set (using test defaults)")
    
    return True


def check_project_structure():
    """Check for required project directories."""
    print("\n🔍 Checking project structure...")
    
    required_dirs = ['core', 'tests', '.github/workflows']
    required_files = ['requirements.txt', 'Dockerfile']
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ⚠️  {dir_path}/: missing")
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️  {file_path}: missing")
    
    return True


def main():
    """Run all environment checks."""
    print("\n" + "="*50)
    print("🔧 Content Factory Environment Checker")
    print("="*50)
    
    checks = [
        check_system_deps,
        check_python_packages,
        check_env_vars,
        check_project_structure,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error during {check.__name__}: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    if all(results):
        print("✅ All checks passed!")
    else:
        print("⚠️  Some checks had warnings")
    print("="*50 + "\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
