#!/usr/bin/env python3
"""
Jira Ticket Branch Creator
 
Fetches Jira tickets and creates git branches based on user selection.
"""
 
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
 
from dotenv import load_dotenv
from jira import JIRA, Issue
import git
import questionary
 
 
def load_config(config_path: str = "config.json") -> Dict:
    """Load configuration from JSON file."""
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"❌ Error: {config_path} not found!")
        sys.exit(1)
    try:
        with open(config_file) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {config_path}: {e}")
        sys.exit(1)
 
 
def load_env(env_path: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_file = Path(env_path)
    if not env_file.exists():
        print(f"❌ Error: {env_path} not found!")
        sys.exit(1)
    load_dotenv(dotenv_path=env_file)
    required_vars = ["JIRA_USERNAME", "JIRA_API_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    return {
        "username": os.getenv("JIRA_USERNAME"),
        "api_token": os.getenv("JIRA_API_TOKEN")
    }
 
 
def connect_to_jira(config: Dict, credentials: Dict[str, str]) -> JIRA:
    """Establish connection to Jira instance."""
    server = config.get("jira_server")
    if not server:
        print("❌ Error: 'jira_server' not found in config.json")
        sys.exit(1)
    try:
        jira = JIRA(server=server, basic_auth=(credentials["username"], credentials["api_token"]))
        jira.myself()  # Test connection
        return jira
    except Exception as e:
        print(f"❌ Error connecting to Jira: {e}")
        sys.exit(1)
 
 
def build_jql_query(config: Dict, username: str) -> str:
    """Build JQL query for fetching tickets."""
    conditions = [f"assignee = '{username}'"]
    if config.get("project_keys"):
        projects = ", ".join([f'"{p}"' for p in config["project_keys"]])
        conditions.append(f"project in ({projects})")
    if config.get("ticket_statuses"):
        statuses = ", ".join([f'"{s}"' for s in config["ticket_statuses"]])
        conditions.append(f"status in ({statuses})")
    if config.get("additional_jql"):
        conditions.append(config["additional_jql"])
    return " AND ".join(conditions)
 
 
def fetch_user_tickets(jira: JIRA, config: Dict, credentials: Dict) -> List[Issue]:
    """Fetch tickets assigned to the user."""
    username = config.get("jira_username", credentials["username"])
    jql = build_jql_query(config, username)
    try:
        max_results = config.get("max_results", 50)
        return jira.search_issues(jql, maxResults=max_results)
    except Exception as e:
        print(f"❌ Error fetching tickets: {e}")
        sys.exit(1)
 
 
def sanitize_branch_name(name: str, max_length: int = 60) -> str:
    """Sanitize string for use as git branch name."""
    name = name.lower().replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^a-z0-9-/]", "", name)  # Keep only safe characters
    name = re.sub(r"-+", "-", name)  # Remove consecutive hyphens
    name = name.strip("-")
    if len(name) > max_length:
        # Preserve ticket key if present
        parts = name.split("-", 1)
        if len(parts) > 1 and len(parts[0]) <= 10:
            ticket_key, summary = parts
            summary = summary[:max_length - len(ticket_key) - 1]
            name = f"{ticket_key}-{summary}".rstrip("-")
        else:
            name = name[:max_length].rstrip("-")
    return name
 
 
def generate_branch_name(ticket: Issue, config: Dict) -> str:
    """Generate branch name based on ticket and config."""
    # Get components
    issue_type = ticket.fields.issuetype.name
    # Branch type prefix
    branch_prefixes = config.get("branch_prefixes", {})
    branch_type = branch_prefixes.get(issue_type, "feature")
    # Ticket key with configurable case
    ticket_key = ticket.key
    case_setting = config.get("ticket_code_case", "lower")
    if case_setting == "lower":
        ticket_key = ticket_key.lower()
    elif case_setting == "upper":
        ticket_key = ticket_key.upper()
    # If any other value, keep original case
    # Sanitized summary
    summary = sanitize_branch_name(ticket.fields.summary)
    # Get pattern from config
    pattern = config.get("branch_pattern", "{type}/{ticket_key}-{summary}")
    # Apply pattern
    try:
        branch_name = pattern.format(
            type=branch_type,
            ticket_key=ticket_key,
            summary=summary
        )
    except KeyError as e:
        print(f"⚠️  Warning: Invalid placeholder {e} in branch pattern")
        # Fallback to simple format
        branch_name = f"{ticket_key}-{summary}"
    # If prefixes disabled, remove the type prefix
    if not config.get("use_branch_prefixes", True):
        # Remove type/ or type- prefix
        branch_name = re.sub(r'^[^/]+/', '', branch_name)  # Remove prefix before /
        branch_name = re.sub(r'^[^-]+-', '', branch_name, count=1)  # Remove prefix before first -
    # Clean up the result
    branch_name = re.sub(r'[-]+', '-', branch_name)  # Remove duplicate hyphens
    branch_name = branch_name.strip('-')
    return branch_name
 
 
def get_git_repo() -> git.Repo:
    """Get the current git repository."""
    try:
        return git.Repo(".")
    except git.exc.InvalidGitRepositoryError:
        print("❌ Error: Not in a git repository!")
        sys.exit(1)
 
 
def check_working_directory_clean(repo: git.Repo) -> bool:
    """Check if working directory is clean."""
    if repo.is_dirty():
        print("⚠️  Warning: You have uncommitted changes.")
        return questionary.confirm("Proceed anyway?", default=False).ask()
    return True
 
 
def handle_branch_creation(repo: git.Repo, branch_name: str):
    """Create or checkout branch based on user preference."""
    if branch_name in [b.name for b in repo.branches]:
        print(f"\n⚠️  Branch '{branch_name}' already exists.")
        action = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("Checkout existing branch", value="checkout"),
                questionary.Choice("Cancel", value="cancel")
            ]
        ).ask()
        if action == "checkout":
            repo.git.checkout(branch_name)
            print(f"✅ Checked out existing branch: {branch_name}")
        else:
            print("\n❌ Operation cancelled.")
            sys.exit(0)
    else:
        try:
            new_branch = repo.create_head(branch_name, repo.active_branch)
            new_branch.checkout()
            print(f"✅ Created and checked out new branch: {branch_name}")
        except Exception as e:
            print(f"❌ Error creating branch: {e}")
            sys.exit(1)
 
 
def display_tickets(tickets: List[Issue]) -> Optional[Issue]:
    """Display tickets and prompt user for selection."""
    if not tickets:
        print("No tickets found.")
        return None
    choices = []
    for idx, ticket in enumerate(tickets, 1):
        summary = ticket.fields.summary[:57] + "..." if len(ticket.fields.summary) > 60 else ticket.fields.summary
        choices.append(
            questionary.Choice(
                title=f"{idx:2d}. {ticket.key} - {summary} [{ticket.fields.status.name}]",
                value=ticket
            )
        )
    choices.append(questionary.Choice(title="❌ Cancel", value=None))
    return questionary.select(
        "Select a ticket to create a branch for:",
        choices=choices,
        instruction="Use arrow keys to navigate, Enter to select"
    ).ask()
 
 
def main():
    """Main execution function."""
    print("🔧 Jira Ticket Branch Creator")
    print("=" * 50)
    # Load config and credentials
    config = load_config()
    credentials = load_env()
    # Connect to Jira
    print("\n📡 Connecting to Jira...")
    jira = connect_to_jira(config, credentials)
    print("✅ Successfully connected to Jira")
    # Fetch tickets
    print(f"\n📋 Fetching tickets for {credentials['username']}...")
    tickets = fetch_user_tickets(jira, config, credentials)
    print(f"✅ Found {len(tickets)} ticket(s)")
    # Select ticket
    selected_ticket = display_tickets(tickets)
    if not selected_ticket:
        print("\n❌ Operation cancelled.")
        sys.exit(0)
    # Generate branch name
    branch_name = generate_branch_name(selected_ticket, config)
    # Confirm/Edit branch name
    print(f"\n🌿 Generated branch name: {branch_name}")
    confirmed_name = questionary.text(
        "Edit branch name if needed (or press Enter to accept):",
        default=branch_name
    ).ask()
    if not confirmed_name:
        print("\n❌ Operation cancelled.")
        sys.exit(0)
    # Get git repo and check status
    repo = get_git_repo()
    if not check_working_directory_clean(repo):
        print("\n❌ Operation cancelled.")
        sys.exit(0)
    # Create/checkout branch
    handle_branch_creation(repo, confirmed_name)
    # Print summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"   Ticket: {selected_ticket.key}")
    print(f"   Summary: {selected_ticket.fields.summary}")
    print(f"   Type: {selected_ticket.fields.issuetype.name}")
    print(f"   Status: {selected_ticket.fields.status.name}")
    print(f"   Branch: {confirmed_name}")
    print("=" * 50)
 
 
if __name__ == "__main__":
    main()
