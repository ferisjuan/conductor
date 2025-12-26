"""
Help text for Conductor CLI
"""

DESCRIPTION = """Conductor - Jira Ticket Branch Creator

A developer workflow tool that integrates Jira tickets with Git branch creation."""

EPILOG = """
Examples:
  conductor --setup       Run initial setup or reconfigure Jira credentials
  conductor -b            Create a branch from a Jira ticket
  conductor --branch      Create a branch from a Jira ticket
  conductor -h            Show this help message
  conductor --help        Show this help message

Description:
  Conductor helps developers quickly create Git branches based on their
  assigned Jira tickets. It fetches your tickets from the current sprint,
  lets you select one, and automatically creates a properly formatted
  branch name.

Getting Started:
  1. Run 'conductor --setup' to configure your Jira credentials
  2. Navigate to any git repository
  3. Run 'conductor -b' to create a branch from your Jira tickets

Configuration:
  After setup, you can manually edit the configuration files:
    - config.json   : Jira settings, projects, statuses, branch patterns
    - .env          : API token (keep this secure)
"""

SETUP_HELP = "Run setup to configure Jira credentials and settings"
BRANCH_HELP = "Create a git branch from a Jira ticket"
