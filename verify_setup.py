#!/usr/bin/env python
"""Setup Verification Script"""

import sys
import importlib
from typing import Tuple, List, Dict, Optional

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is 3.10 or higher (pyproject.toml's requires-python)."""
    version = sys.version_info
    if version >= (3, 10):
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)"


def check_package(package_name: str, min_version: Optional[str] = None) -> Tuple[bool, str]:
    """Check if a package is installed and optionally verify minimum version."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")

        if min_version and version != "unknown":
            try:
                from packaging import version as pkg_version

                if pkg_version.parse(version) < pkg_version.parse(min_version):
                    return False, f"{package_name} {version} (requires {min_version}+)"
            except Exception:
                pass

        return True, f"{package_name} {version}"
    except ModuleNotFoundError as e:
        # Only "not installed" when the module that is missing is this package (or a parent of a dotted name). A
        # package that is installed but needs another absent module raises the same class, with that module's name.
        if e.name is not None and (e.name == package_name or package_name.startswith(f"{e.name}.")):
            return False, f"{package_name} not installed"
        return False, f"{package_name} failed to import: {e}"
    except Exception as e:
        # A plain ImportError (a missing native library), or a numpy/pandas binary mismatch raising OSError,
        # ValueError, ... : the package is there but broken.
        return False, f"{package_name} failed to import: {e}"


def verify_dependencies() -> Dict[str, List[Tuple[str, bool, str]]]:
    """Verify all required and optional dependencies."""
    required_packages = [
        ("streamlit", "1.54.0"),
        ("pandas", "2.3.3"),
        ("plotly", "6.5.0"),
        ("numpy", "2.2.6"),
        ("faker", None),
        ("pytest", "9.0.3"),
    ]

    optional_packages = [
        ("kaleido", None),
    ]

    results: Dict[str, List[Tuple[str, bool, str]]] = {"required": [], "optional": []}

    for package_name, min_version in required_packages:
        success, message = check_package(package_name, min_version)
        results["required"].append((package_name, success, message))

    for package_name, min_version in optional_packages:
        success, message = check_package(package_name, min_version)
        results["optional"].append((package_name, success, message))

    return results


def check_project_structure() -> List[Tuple[str, bool, str]]:
    """Check if project directories and files exist."""
    import os

    required_items = [
        ("app.py", "file"),
        ("requirements.txt", "file"),
        ("utils/", "directory"),
        ("utils/cleaner.py", "file"),
        ("utils/data_generator.py", "file"),
        ("utils/health_metrics.py", "file"),
        ("utils/visualizer.py", "file"),
        ("utils/ui_helpers.py", "file"),
        ("components/", "directory"),
        ("components/sidebar.py", "file"),
        ("components/kpi_display.py", "file"),
        ("components/comparison.py", "file"),
        ("components/tab_preparation.py", "file"),
        ("components/tab_analytics.py", "file"),
        ("components/tab_explorer.py", "file"),
        ("tests/", "directory"),
    ]

    results = []

    for item, item_type in required_items:
        if item_type == "file":
            exists = os.path.isfile(item)
        else:
            exists = os.path.isdir(item)

        message = f"{item} ({'✓' if exists else '✗'})"
        results.append((item, exists, message))

    return results


def test_imports() -> List[Tuple[str, bool, str]]:
    """Test importing project modules."""
    modules = [
        "utils.cleaner",
        "utils.data_generator",
        "utils.health_metrics",
        "utils.visualizer",
        "utils.ui_helpers",
        "components.sidebar",
        "components.kpi_display",
        "components.comparison",
        "components.tab_preparation",
        "components.tab_analytics",
        "components.tab_explorer",
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


def main():  # noqa: C901
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

    for package, success, message in dep_results["required"]:
        print_result(package, success, message)
        if not success:
            all_checks_passed = False

    print_section("Optional Dependencies")
    for package, success, message in dep_results["optional"]:
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
        print("  - Ensure Python 3.10+ is installed")
        print("  - Run from the project root directory\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
