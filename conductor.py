#!/usr/bin/env python3
"""
Conductor - Main CLI entry point

Usage:
  conductor --setup    Configure Jira credentials and settings
  conductor -b         Create a git branch from a Jira ticket
  conductor -h         Show help
"""

import argparse
import sys
import importlib


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = {
        "jira": "jira",
        "questionary": "questionary",
        "git": "GitPython",
        "dotenv": "python-dotenv",
        "requests": "requests",
    }
    missing_packages = []
    for import_name, package_name in required_packages.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print("Error: The following required packages are not installed:")
        for package in missing_packages:
            print(f"- {package}")
        print("\nPlease install them by running:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)



def main():
    """Main entry point for conductor CLI."""
    check_dependencies()

    from cli_help import DESCRIPTION, EPILOG, SETUP_HELP, BRANCH_HELP
    parser = argparse.ArgumentParser(
        prog='conductor',
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG
    )

    parser.add_argument(
        '--setup',
        action='store_true',
        help=SETUP_HELP
    )

    parser.add_argument(
        '-b', '--branch',
        action='store_true',
        help=BRANCH_HELP
    )

    parser.add_argument(
        '--update',
        action='store_true',
        help='Check for updates and install the latest version'
    )

    parser.add_argument(
        '--delete-app',
        action='store_true',
        help='Remove all Conductor files and directories from your system'
    )

    args = parser.parse_args()

    # Handle --delete-app flag
    if args.delete_app:
        from conductor_delete import main as delete_main
        delete_main()
        sys.exit(0)


    # Handle --update flag
    if args.update:
        from conductor_update import main as update_main
        update_main()
        sys.exit(0)

    # Handle --setup flag
    if args.setup:
        from conductor_setup import main as setup_main
        setup_main()
        sys.exit(0)

    # Handle -b/--branch flag (create branch)
    if args.branch:
        from jira_branch_creator import main as branch_creator_main
        branch_creator_main()
        sys.exit(0)

    # If no flags provided, show help
    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
