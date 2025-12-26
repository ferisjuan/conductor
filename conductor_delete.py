#!/usr/bin/env python3
"""
Conductor Uninstaller

Removes all Conductor files and directories from the system.
"""

import shutil
import sys
from pathlib import Path

import questionary

from settings import CONDUCTOR_HOME


def main():
    """Main uninstallation function."""
    print("Conductor Uninstaller")
    print("=" * 50)
    print("This will permanently remove Conductor from your system.")
    print("This action cannot be undone.")
    print("\nFiles and directories to be removed:")
    print(f"  - Installation directory: {CONDUCTOR_HOME}")
    print(
        "  - Commands: {{'~/.local/bin/conductor', '~/.local/bin/conductor-setup', '~/.local/bin/conductor-update'}}"
    )
    print("=" * 50)

    confirmation_text = "confirm-deletion"

    try:
        user_confirmation = questionary.text(
            f"To confirm, please type the following text exactly: {confirmation_text}",
            validate=lambda text: text == confirmation_text
            or f"You must type '{confirmation_text}' to confirm.",
        ).ask()

        if user_confirmation != confirmation_text:
            print("\nDeletion cancelled.")
            sys.exit(0)

        print("\nProceeding with uninstallation...")

        # 1. Remove the installation directory
        if CONDUCTOR_HOME.exists():
            print(f"Removing {CONDUCTOR_HOME}...")
            shutil.rmtree(CONDUCTOR_HOME)
            print("✅ Installation directory removed.")
        else:
            print("✅ Installation directory already removed.")

        # 2. Remove the command shortcuts
        bin_dir = Path.home() / ".local" / "bin"
        commands_to_remove = ["conductor", "conductor-setup", "conductor-update"]

        for command in commands_to_remove:
            command_path = bin_dir / command
            if command_path.exists():
                print(f"Removing {command_path}...")
                command_path.unlink()
                print(f"✅ {command} command removed.")
            else:
                print(f"✅ {command} command already removed.")

        print("\n✅ Conductor has been successfully uninstalled.")

    except (KeyboardInterrupt, TypeError):
        print("\nDeletion cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ An error occurred during uninstallation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
