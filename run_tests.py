#!/usr/bin/env python3
"""Test runner script for git-memory."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite."""
    project_root = Path(__file__).parent
    
    print("🧪 Running git-memory test suite...")
    print("=" * 50)
    
    # Install test dependencies if needed
    print("📦 Installing test dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-e", ".[test]"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to install dependencies: {result.stderr}")
        return False
    
    # Run pytest
    print("▶️  Running tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "-v"
    ], cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


def run_specific_tests():
    """Run specific test categories."""
    project_root = Path(__file__).parent
    
    print("🧪 Test Categories Available:")
    print("1. Unit tests only (fast)")
    print("2. Integration tests only (slower)")
    print("3. All tests")
    print("4. Coverage report")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        cmd = [sys.executable, "-m", "pytest", "-v", "-m", "not integration"]
    elif choice == "2":
        cmd = [sys.executable, "-m", "pytest", "-v", "-m", "integration"]
    elif choice == "3":
        cmd = [sys.executable, "-m", "pytest", "-v"]
    elif choice == "4":
        cmd = [sys.executable, "-m", "pytest", "--cov=git_memory", "--cov-report=html", "--cov-report=term"]
    else:
        print("Invalid choice!")
        return False
    
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        success = run_specific_tests()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)