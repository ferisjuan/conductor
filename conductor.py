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

from cli_help import DESCRIPTION, EPILOG, SETUP_HELP, BRANCH_HELP


def main():
    """Main entry point for conductor CLI."""
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

    args = parser.parse_args()

    # Handle --setup flag
    if args.setup:
        from setup import main as setup_main
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
