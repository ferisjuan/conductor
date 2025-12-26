#!/usr/bin/env python3
"""
Version checking and update utilities for Conductor.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import requests

# Current version - this should match pyproject.toml
__version__ = "1.0.6"

# Configuration
GITHUB_REPO = "ferisjuan/conductor"
VERSION_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
INSTALL_DIR = Path.home() / ".conductor"
VERSION_CACHE_FILE = INSTALL_DIR / ".version_cache"
CHECK_INTERVAL_DAYS = 1


def get_current_version() -> str:
    """Get the current installed version."""
    return __version__


def get_latest_version() -> Optional[str]:
    """Fetch the latest version from GitHub releases."""
    try:
        response = requests.get(VERSION_CHECK_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Remove 'v' prefix if present
            version = data.get("tag_name", "").lstrip("v")
            return version
    except Exception:
        # Silently fail if we can't check for updates
        pass
    return None


def parse_version(version: str) -> Tuple[int, ...]:
    """Parse version string into tuple of integers for comparison."""
    try:
        return tuple(int(x) for x in version.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def is_newer_version(current: str, latest: str) -> bool:
    """Check if latest version is newer than current."""
    return parse_version(latest) > parse_version(current)


def should_check_for_updates() -> bool:
    """Determine if enough time has passed to check for updates."""
    if not VERSION_CACHE_FILE.exists():
        return True

    try:
        with open(VERSION_CACHE_FILE, "r") as f:
            cache = json.load(f)

        last_check = datetime.fromisoformat(cache.get("last_check", "2000-01-01"))
        return datetime.now() - last_check > timedelta(days=CHECK_INTERVAL_DAYS)
    except Exception:
        return True


def save_version_check() -> None:
    """Save the timestamp of the last version check."""
    try:
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        cache = {
            "last_check": datetime.now().isoformat(),
            "current_version": get_current_version(),
        }
        with open(VERSION_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def check_for_updates(silent: bool = False) -> Optional[str]:
    """
    Check for updates and return the latest version if newer.

    Args:
        silent: If True, don't perform the check (used when updates are disabled)

    Returns:
        Latest version string if update available, None otherwise
    """
    if silent or not should_check_for_updates():
        return None

    current = get_current_version()
    latest = get_latest_version()

    # Save check timestamp
    save_version_check()

    if latest and is_newer_version(current, latest):
        return latest

    return None


def print_update_message(latest_version: str) -> None:
    """Print a friendly update notification."""
    current = get_current_version()

    print("\n" + "=" * 60)
    print(f"🎉 New version available: v{latest_version} (current: v{current})")
    print("=" * 60)
    print("\n📦 Update with one of these commands:")
    print(
        f"\n   curl -fsSL https://raw.githubusercontent.com/{GITHUB_REPO}/main/install.sh | bash"
    )
    print("\n   Or if installed via uv:")
    print("   conductor-update")
    print("\n💡 See what's new:")
    print(f"   https://github.com/{GITHUB_REPO}/releases/latest")
    print("=" * 60 + "\n")


def get_install_method() -> str:
    """Detect how Conductor was installed."""
    # Check if running from a uv-managed environment
    if os.getenv("VIRTUAL_ENV") or os.getenv("UV_PROJECT_ENVIRONMENT"):
        return "uv"

    # Check if installed via pip (site-packages)
    try:
        import conductor

        if "site-packages" in conductor.__file__:
            return "pip"
    except (ImportError, AttributeError):
        pass

    # Default to script installation
    return "script"


def main():
    """Command-line interface for version checking."""
    import argparse

    parser = argparse.ArgumentParser(description="Check Conductor version")
    parser.add_argument("--current", action="store_true", help="Show current version")
    parser.add_argument("--latest", action="store_true", help="Check latest version")
    parser.add_argument("--check", action="store_true", help="Check for updates")

    args = parser.parse_args()

    if args.current:
        print(f"Conductor v{get_current_version()}")
    elif args.latest:
        latest = get_latest_version()
        if latest:
            print(f"Latest version: v{latest}")
        else:
            print("Could not fetch latest version")
    elif args.check:
        current = get_current_version()
        latest = get_latest_version()

        print(f"Current version: v{current}")
        if latest:
            print(f"Latest version:  v{latest}")
            if is_newer_version(current, latest):
                print("\n✨ Update available!")
                print_update_message(latest)
            else:
                print("\n✅ You're up to date!")
        else:
            print("Could not check for updates")
    else:
        print(f"Conductor v{get_current_version()}")
        print(f"\nInstall method: {get_install_method()}")


if __name__ == "__main__":
    main()
