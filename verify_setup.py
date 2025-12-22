#!/usr/bin/env python
"""
Setup Verification Script

This script verifies that all required dependencies are installed correctly
and the environment is ready to run Community Pulse.

Run this script after installation to ensure everything is set up properly:
    python verify_setup.py
"""

import sys
import importlib
from typing import Tuple, List, Dict

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is 3.9 or higher."""
    version = sys.version_info
    if version >= (3, 9):
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)"


def check_package(package_name: str, min_version: str = None) -> Tuple[bool, str]:
    """
    Check if a package is installed and optionally verify minimum version.
    
    Args:
        package_name: Name of the package to check
        min_version: Minimum required version (optional)
    
    Returns:
        Tuple of (success, message)
    """
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        
        if min_version and version != 'unknown':
            try:
                from packaging import version as pkg_version
                if pkg_version.parse(version) < pkg_version.parse(min_version):
                    return False, f"{package_name} {version} (requires {min_version}+)"
            except Exception:
                # If version comparison fails, just report the version
                pass
        
        return True, f"{package_name} {version}"
    except ImportError:
        return False, f"{package_name} not installed"


def verify_dependencies() -> Dict[str, List[Tuple[str, bool, str]]]:
    """
    Verify all required and optional dependencies.
    
    Returns:
        Dictionary with 'required' and 'optional' dependency check results
    """
    # Required dependencies
    required_packages = [
        ('streamlit', '1.52.2'),
        ('pandas', '2.2.2'),
        ('plotly', '6.5.0'),
        ('numpy', '1.26.4'),
        ('faker', None),
        ('pytest', None),
        ('Levenshtein', None),  # python-Levenshtein
    ]
    
    # Optional dependencies
    optional_packages = [
        ('kaleido', None),  # For static image export
    ]
    
    results = {
        'required': [],
        'optional': []
    }
    
    # Check required packages
    for package_name, min_version in required_packages:
        success, message = check_package(package_name, min_version)
        results['required'].append((package_name, success, message))
    
    # Check optional packages
    for package_name, min_version in optional_packages:
        success, message = check_package(package_name, min_version)
        results['optional'].append((package_name, success, message))
    
    return results


def check_project_structure() -> List[Tuple[str, bool, str]]:
    """Check if project directories and files exist."""
    import os
    
    required_items = [
        ('app.py', 'file'),
        ('requirements.txt', 'file'),
        ('utils/', 'directory'),
        ('utils/cleaner.py', 'file'),
        ('utils/data_generator.py', 'file'),
        ('utils/health_metrics.py', 'file'),
        ('utils/visualizer.py', 'file'),
        ('utils/ui_helpers.py', 'file'),
        ('tests/', 'directory'),
    ]
    
    results = []
    
    for item, item_type in required_items:
        if item_type == 'file':
            exists = os.path.isfile(item)
        else:
            exists = os.path.isdir(item)
        
        message = f"{item} ({'✓' if exists else '✗'})"
        results.append((item, exists, message))
    
    return results


def test_imports() -> List[Tuple[str, bool, str]]:
    """Test importing project modules."""
    modules = [
        'utils.cleaner',
        'utils.data_generator',
        'utils.health_metrics',
        'utils.visualizer',
        'utils.ui_helpers',
    ]
    
    results = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            results.append((module, True, f"{module} imports successfully"))
        except Exception as e:
            results.append((module, False, f"{module} failed: {str(e)}"))
    
    return results


def print_section(title: str):
    """Print a section header."""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_result(name: str, success: bool, message: str):
    """Print a check result with color coding."""
    status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
    print(f"  {status} {message}")


def main():
    """Run all verification checks."""
    print(f"\n{BOLD}Community Pulse - Setup Verification{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    
    all_checks_passed = True
    
    # Check Python version
    print_section("Python Version")
    success, message = check_python_version()
    print_result("Python", success, message)
    if not success:
        all_checks_passed = False
    
    # Check dependencies
    print_section("Required Dependencies")
    dep_results = verify_dependencies()
    
    for package, success, message in dep_results['required']:
        print_result(package, success, message)
        if not success:
            all_checks_passed = False
    
    print_section("Optional Dependencies")
    for package, success, message in dep_results['optional']:
        print_result(package, success, message)
        if not success:
            print(f"    {YELLOW}Note: Optional dependency. Some features may not work.{RESET}")
    
    # Check project structure
    print_section("Project Structure")
    structure_results = check_project_structure()
    for item, success, message in structure_results:
        print_result(item, success, message)
        if not success:
            all_checks_passed = False
    
    # Test module imports
    print_section("Module Imports")
    import_results = test_imports()
    for module, success, message in import_results:
        print_result(module, success, message)
        if not success:
            all_checks_passed = False
    
    # Final summary
    print_section("Summary")
    if all_checks_passed:
        print(f"  {GREEN}{BOLD}✓ All checks passed! Your environment is ready.{RESET}\n")
        print(f"  {BLUE}You can now run the application with:{RESET}")
        print(f"  {BOLD}streamlit run app.py{RESET}\n")
        return 0
    else:
        print(f"  {RED}{BOLD}✗ Some checks failed. Please fix the issues above.{RESET}\n")
        print(f"  {YELLOW}Common fixes:{RESET}")
        print(f"  - Install missing packages: {BOLD}pip install -r requirements.txt{RESET}")
        print(f"  - Ensure Python 3.9+ is installed")
        print(f"  - Run from the project root directory\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
