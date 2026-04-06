#!/usr/bin/env python3
"""
Automated publishing script for metakitchen package.

This script handles:
- Version management in metak.py and pyproject.toml
- Building the package
- Publishing to Test PyPI or PyPI

Usage:
    python publish.py [test|release]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


class PublishError(Exception):
    """Custom exception for publishing errors."""

    pass


class MetakitchenPublisher:
    """Handles the publishing workflow for metakitchen package."""

    PACKAGE_NAME = "metakitchen"

    def __init__(self, mode: str = "test", skip_tests: bool = False):
        self.mode = mode
        self.skip_tests = skip_tests
        self.root_path = Path(__file__).parent
        self.version_file = self.root_path / "metak.py"
        self.pyproject_file = self.root_path / "pyproject.toml"
        self.python_exe = sys.executable

        # Validate files exist
        if not self.version_file.exists():
            raise PublishError(f"metak.py not found at {self.version_file}")
        if not self.pyproject_file.exists():
            raise PublishError(f"pyproject.toml not found at {self.pyproject_file}")

    def get_current_version(self) -> str:
        """Extract current version from metak.py."""
        content = self.version_file.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            raise PublishError("Could not find __version__ in metak.py")
        return match.group(1)

    def validate_version(self, version: str) -> bool:
        """Validate version string format (major.minor.patch)."""
        pattern = r"^\d+\.\d+\.\d+$"
        return bool(re.match(pattern, version))

    def increment_patch_version(self, version: str) -> str:
        """Increment the patch version number."""
        parts = version.split(".")
        if len(parts) != 3:
            raise PublishError(f"Invalid version format: {version}")

        try:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            return f"{major}.{minor}.{patch + 1}"
        except ValueError:
            raise PublishError(f"Invalid version format: {version}")

    def get_new_version(self, current_version: str) -> str:
        """Prompt user for new version or auto-increment."""
        print(f"\nCurrent version: {current_version}")
        print("Options:")
        print("1. Press Enter to auto-increment patch version")
        print("2. Enter a specific version (format: major.minor.patch)")

        user_input = input(
            "\nEnter new version (or press Enter for auto-increment): "
        ).strip()

        if not user_input:
            new_version = self.increment_patch_version(current_version)
            print(f"Auto-incrementing to: {new_version}")
            return new_version

        if not self.validate_version(user_input):
            raise PublishError(
                f"Invalid version format: {user_input}. Use major.minor.patch (e.g., 1.2.3)"
            )

        return user_input

    def version_exists_on_pypi(self, version: str) -> bool:
        """Check if the given version exists on PyPI or Test PyPI."""
        try:
            import urllib.request
            import json as json_mod

            if self.mode == "test":
                url = f"https://test.pypi.org/pypi/{self.PACKAGE_NAME}/json"
            else:
                url = f"https://pypi.org/pypi/{self.PACKAGE_NAME}/json"

            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_mod.loads(resp.read().decode())
                return version in data.get("releases", {})
        except Exception:
            return False

    def update_version_in_file(self, filepath: Path, new_version: str) -> None:
        """Update version string in a file."""
        content = filepath.read_text(encoding="utf-8")

        new_content = re.sub(
            r'((?:__)?version(?:__)?\s*=\s*)["\'][^"\']+["\']',
            f'\\1"{new_version}"',
            content,
            count=1,
        )

        if new_content == content:
            raise PublishError(f"Could not update version in {filepath}")

        filepath.write_text(new_content, encoding="utf-8")
        print(f"  Updated version in {filepath.name}")

    def run_command_with_streaming(
        self, command: list, description: str, cwd: Optional[Path] = None
    ) -> None:
        """Run a command with real-time output streaming."""
        print(f"\n>> {description}...")
        print(f"   Running: {' '.join(command)}")

        try:
            process = subprocess.Popen(
                command,
                cwd=cwd or self.root_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            for line in process.stdout:
                print(line, end="")

            return_code = process.wait()

            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)

        except subprocess.CalledProcessError as e:
            print(f"\n   ERROR: {description} failed")
            print(f"   Return code: {e.returncode}")
            raise PublishError(f"{description} failed with return code {e.returncode}")

        print(f"   {description} completed successfully")

    def build_package(self) -> None:
        """Build the package wheel and source distribution."""
        # Clean previous builds
        dist_path = self.root_path / "dist"
        if dist_path.exists():
            import shutil

            shutil.rmtree(dist_path)
            print("  Cleaned previous build artifacts")

        self.run_command_with_streaming(
            [self.python_exe, "-m", "build"], "Building package"
        )

    def check_package(self) -> None:
        """Check the built package with twine."""
        self.run_command_with_streaming(
            ["twine", "check", "dist/*"], "Checking package with twine"
        )

    def upload_package(self, new_version: str) -> None:
        """Upload package to PyPI or Test PyPI."""
        target = "Test PyPI" if self.mode == "test" else "PyPI"

        print(f"\n   About to upload version {new_version} to {target}")

        if self.mode == "release":
            print(
                "   WARNING: This will upload to the REAL PyPI! This action cannot be undone."
            )

        confirm = (
            input(f"Are you sure you want to upload to {target}? (yes/y/no/n): ")
            .strip()
            .lower()
        )

        if confirm not in ["yes", "y"]:
            print("   Upload cancelled by user")
            sys.exit(0)

        if self.mode == "test":
            command = ["twine", "upload", "--repository", "testpypi", "dist/*"]
        else:
            command = ["twine", "upload", "dist/*"]

        self.run_command_with_streaming(command, f"Uploading to {target}")

        print(f"\n   Successfully uploaded to {target}!")
        if self.mode == "test":
            print("\nTo test the package, run:")
            print(
                f"pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ {self.PACKAGE_NAME}=={new_version}"
            )
        else:
            print("\nTo install the package, run:")
            print(f"pip install {self.PACKAGE_NAME}=={new_version}")

    def publish(self) -> None:
        """Main publishing workflow."""
        try:
            print(f"Publishing {self.PACKAGE_NAME} (mode: {self.mode})")

            # Get current version
            current_version = self.get_current_version()

            # Get new version from user
            new_version = self.get_new_version(current_version)

            # Check if version exists on PyPI/TestPyPI
            if self.version_exists_on_pypi(new_version):
                print(
                    f"\n   ERROR: Version {new_version} already exists on the target PyPI repository. Aborting."
                )
                sys.exit(1)

            # Update version in both files
            self.update_version_in_file(self.version_file, new_version)
            self.update_version_in_file(self.pyproject_file, new_version)

            # Build package
            self.build_package()

            # Check package
            self.check_package()

            # Upload package
            self.upload_package(new_version)

        except PublishError as e:
            print(f"\n   Publishing failed: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n   Publishing cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n   Unexpected error: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Publish {MetakitchenPublisher.PACKAGE_NAME} package to PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python publish.py                    # Publish to Test PyPI (default)
  python publish.py test               # Publish to Test PyPI
  python publish.py release            # Publish to PyPI (production)
        """,
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["test", "release"],
        default="test",
        help="Publishing mode: 'test' for Test PyPI, 'release' for PyPI (default: test)",
    )

    args = parser.parse_args()

    # Verify we're in the right directory
    if not Path("pyproject.toml").exists():
        print(
            "ERROR: pyproject.toml not found. Please run this script from the project root."
        )
        sys.exit(1)

    # Check required tools are installed
    missing_tools = []

    # Check twine
    try:
        subprocess.run(["twine", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append("twine")

    # Check build (as python module)
    try:
        subprocess.run(
            [sys.executable, "-m", "build", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append("build")

    if missing_tools:
        print(f"ERROR: Missing required tools: {', '.join(missing_tools)}")
        print(f"Install them with: pip install {' '.join(missing_tools)}")
        sys.exit(1)

    # Create publisher and run
    publisher = MetakitchenPublisher(args.mode)
    publisher.publish()


if __name__ == "__main__":
    main()
