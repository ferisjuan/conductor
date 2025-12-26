#!/usr/bin/env python3
"""
Conductor - Jira Ticket Branch Creator

Fetches Jira tickets and creates git branches based on user selection.
Filters tickets to only show those in the current sprint.
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


from settings import CONDUCTOR_HOME


def load_config(config_path: Optional[str] = None) -> Dict:
    """Load configuration from JSON file."""
    if config_path is None:
        # Use default location in user's home directory
        config_path = CONDUCTOR_HOME / "config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        print(f"Error: {config_path} not found!")
        print("Please run 'conductor --setup' to configure Conductor.")
        sys.exit(1)

    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_path}: {e}")
        sys.exit(1)
    
    # Validate required fields (only server and username are now required)
    required_fields = ["jira_server", "jira_username"]
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"Error: Missing required fields in {config_path}: {', '.join(missing_fields)}")
        print("\nRun 'python setup.py' to configure Conductor.")
        sys.exit(1)
    
    # Make optional fields optional
    config.setdefault("project_keys", [])
    config.setdefault("ticket_statuses", [])
    config.setdefault("use_branch_prefixes", True)
    config.setdefault("max_results", 100)  # Increased default
    config.setdefault("branch_prefixes", {
        "Bug": "bugfix",
        "Story": "feature",
        "Task": "feature",
        "Epic": "feature",
        "Improvement": "improvement",
        "Spike": "spike"
    })
    
    return config


def load_env(env_path: Optional[str] = None) -> Dict[str, str]:
    """Load environment variables from .env file."""
    if env_path is None:
        # Use default location in user's home directory
        env_path = CONDUCTOR_HOME / ".env"
    else:
        env_path = Path(env_path)

    if not env_path.exists():
        print(f"Error: {env_path} not found!")
        print("\nRun 'conductor --setup' to configure Conductor.")
        sys.exit(1)

    load_dotenv(dotenv_path=env_path)
    
    required_vars = ["JIRA_API_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("\nRun 'python setup.py' to configure Conductor.")
        sys.exit(1)
    
    return {
        "api_token": os.getenv("JIRA_API_TOKEN")
    }


def connect_to_jira(config: Dict, credentials: Dict[str, str]) -> JIRA:
    """Establish connection to Jira instance."""
    server = config.get("jira_server")
    username = config.get("jira_username")
    
    try:
        jira = JIRA(server=server, basic_auth=(username, credentials["api_token"]))
        jira.myself()  # Test connection
        return jira
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        sys.exit(1)


def build_jql_query(config: Dict) -> str:
    """Build JQL query for fetching tickets in current sprint."""
    username = config.get("jira_username")
    conditions = [f"assignee = '{username}'"]
    
    # Add sprint condition (current sprint)
    conditions.append("sprint in openSprints()")
    
    # Optional project filter
    if config.get("project_keys"):
        projects = ", ".join([f'"{p}"' for p in config["project_keys"]])
        conditions.append(f"project in ({projects})")
    
    # Optional status filter
    if config.get("ticket_statuses"):
        statuses = ", ".join([f'"{s}"' for s in config["ticket_statuses"]])
        conditions.append(f"status in ({statuses})")
    
    if config.get("additional_jql"):
        conditions.append(config["additional_jql"])
    
    return " AND ".join(conditions)


def fetch_user_tickets(jira: JIRA, config: Dict) -> List[Issue]:
    """Fetch tickets assigned to the user in current sprint."""
    jql = build_jql_query(config)
    print(f"\n🔍 Using JQL: {jql}")
    
    try:
        max_results = config.get("max_results", 100)
        
        # First, get total count
        print(f"📊 Fetching tickets (max: {max_results})...")
        tickets = jira.search_issues(jql, maxResults=max_results, startAt=0)
        
        print(f"✅ Found {len(tickets)} ticket(s)")
        
        # Debug: Print first few ticket keys if found
        if tickets:
            print(f"🎫 Sample tickets: {', '.join([t.key for t in tickets[:5]])}")
            if len(tickets) > 5:
                print(f"   ... and {len(tickets) - 5} more")
        
        if len(tickets) == max_results:
            print(f"⚠️  Reached max results limit ({max_results}). Consider increasing 'max_results' in config.json")
        
        # Debug info
        if len(tickets) < 1:
            print("\n⚠️  Only found 2 or fewer tickets. Debugging info:")
            print(f"   - Username: {config.get('jira_username')}")
            print(f"   - Project filter: {config.get('project_keys') or 'None (all projects)'}")
            print(f"   - Status filter: {config.get('ticket_statuses') or 'None (all statuses)'}")
            print(f"   - Sprint filter: sprint in openSprints()")
            print("\n💡 Try these debugging steps:")
            print("   1. Remove project_keys from config.json to search all projects")
            print("   2. Remove ticket_statuses from config.json to search all statuses")
            print("   3. Comment out the sprint filter (line with 'openSprints')")
            print("   4. Run this JQL directly in Jira to verify results:")
            print(f"      {jql}")
        
        return tickets
    except Exception as e:
        print(f"❌ Error fetching tickets: {e}")
        print(f"\n💡 Debug info:")
        print(f"   JQL: {jql}")
        print(f"   Max results: {max_results}")
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
    
    # Ticket key - always keep project key uppercase, apply case to number part
    ticket_key = ticket.key
    case_setting = config.get("ticket_code_case", "lower")
    
    # Split ticket key into project and number (e.g., "CDEM-1234" -> "CDEM", "1234")
    if "-" in ticket_key:
        project_key, ticket_number = ticket_key.split("-", 1)
        # Always keep project key uppercase
        project_key = project_key.upper()
        # Apply case setting to the full key for display
        if case_setting == "lower":
            ticket_key = f"{project_key}-{ticket_number}".lower()
            # But preserve uppercase project in final key
            ticket_key = f"{project_key}-{ticket_number.lower()}"
        elif case_setting == "upper":
            ticket_key = f"{project_key}-{ticket_number}".upper()
        else:
            # Keep original case
            ticket_key = f"{project_key}-{ticket_number}"
    
    # Sanitized summary
    summary = sanitize_branch_name(ticket.fields.summary)
    
    # Check if prefixes are enabled
    use_prefixes = config.get("use_branch_prefixes", True)
    
    if use_prefixes:
        # With prefixes: feature/CDEM-1234-something
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
            print(f"Warning: Invalid placeholder {e} in branch pattern")
            # Fallback to simple format with prefix
            branch_name = f"{branch_type}/{ticket_key}-{summary}"
    else:
        # Without prefixes: CDEM-1234-something (just ticket key and summary)
        branch_name = f"{ticket_key}-{summary}"
    
    # Clean up the result
    branch_name = re.sub(r'[-]+', '-', branch_name)  # Remove duplicate hyphens
    branch_name = branch_name.strip('-')
    
    return branch_name


def get_git_repo() -> git.Repo:
    """Get the current git repository."""
    try:
        return git.Repo(".")
    except git.exc.InvalidGitRepositoryError:
        print("Error: Not in a git repository!")
        sys.exit(1)


def check_working_directory_clean(repo: git.Repo) -> bool:
    """Check if working directory is clean."""
    if repo.is_dirty():
        print("Warning: You have uncommitted changes.")
        return questionary.confirm("Proceed anyway?", default=False).ask()
    return True


def handle_branch_creation(repo: git.Repo, branch_name: str):
    """Create or checkout branch based on user preference."""
    if branch_name in [b.name for b in repo.branches]:
        print(f"\nWarning: Branch '{branch_name}' already exists.")
        action = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("Checkout existing branch", value="checkout"),
                questionary.Choice("Cancel", value="cancel")
            ]
        ).ask()
        
        if action == "checkout":
            repo.git.checkout(branch_name)
            print(f"Checked out existing branch: {branch_name}")
        else:
            print("\nOperation cancelled.")
            sys.exit(0)
    else:
        try:
            new_branch = repo.create_head(branch_name, repo.active_branch)
            new_branch.checkout()
            print(f"Created and checked out new branch: {branch_name}")
        except Exception as e:
            print(f"Error creating branch: {e}")
            sys.exit(1)


def get_status_icon(status_name: str) -> str:
    """Get emoji icon for ticket status."""
    status_lower = status_name.lower()
    
    # Map of status keywords to icons
    status_icons = {
        # In Progress / Working
        "in progress": "🔨",
        "working": "🔨",
        "in development": "🔨",
        "dev": "🔨",
        
        # Ready for work
        "ready for work": "📋",
        "ready for dev": "📋",
        "to do": "📋",
        "todo": "📋",
        "backlog": "📋",
        
        # Review states
        "peer review": "👀",
        "code review": "👀",
        "in review": "👀",
        "review": "👀",
        
        # QA / Testing
        "ready for qa": "🧪",
        "qa": "🧪",
        "testing": "🧪",
        "ready for test": "🧪",
        "in qa": "🧪",
        
        # UAT
        "uat": "🎯",
        "user acceptance": "🎯",
        "ready for uat": "🎯",
        "in uat": "🎯",
        
        # Done / Completed
        "done": "✅",
        "completed": "✅",
        "closed": "✅",
        "resolved": "✅",
        
        # Blocked / On Hold
        "blocked": "🚫",
        "on hold": "⏸️",
        "waiting": "⏳",
    }
    
    # Check for exact or partial matches
    for keyword, icon in status_icons.items():
        if keyword in status_lower:
            return icon
    
    # Default icon for unknown statuses
    return "📌"


def display_tickets(tickets: List[Issue]) -> Optional[Issue]:
    """Display tickets and prompt user for selection."""
    if not tickets:
        print("No tickets found.")
        return None
    
    choices = []
    for idx, ticket in enumerate(tickets, 1):
        # Get status info
        status_name = ticket.fields.status.name
        status_icon = get_status_icon(status_name)
        
        # Truncate summary if needed
        summary = ticket.fields.summary[:50] + "..." if len(ticket.fields.summary) > 53 else ticket.fields.summary
        
        # Format: Icon | Key | Summary | Status
        choices.append(
            questionary.Choice(
                title=f"{idx:2d}. {status_icon} {ticket.key} - {summary} [{status_name}]",
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
    print("Conductor - Jira Ticket Branch Creator")
    print("=" * 50)
    
    # Load config and credentials
    config = load_config()
    credentials = load_env()
    
    # Connect to Jira
    print("\nConnecting to Jira...")
    jira = connect_to_jira(config, credentials)
    print("✅ Successfully connected to Jira")
    
    # Fetch tickets
    print(f"\n🔄 Fetching tickets for {config['jira_username']} in current sprint...")
    tickets = fetch_user_tickets(jira, config)
    
    if not tickets:
        print("\n❌ No tickets found matching the criteria.")
        sys.exit(0)
    
    # Select ticket
    selected_ticket = display_tickets(tickets)
    if not selected_ticket or not hasattr(selected_ticket, 'fields'):
        print("\nOperation cancelled or invalid ticket selected.")
        sys.exit(0)
    
    # Generate branch name (using config setting)
    branch_name = generate_branch_name(selected_ticket, config)
    
    # Confirm/Edit branch name
    prefix_status = "✅ enabled" if config.get("use_branch_prefixes", True) else "❌ disabled"
    print(f"\nGenerated branch name: {branch_name}")
    print(f"Branch prefixes are {prefix_status} (change in config.json if needed)")
    
    confirmed_name = questionary.text(
        "Edit branch name if needed (or press Enter to accept):",
        default=branch_name
    ).ask()
    
    if not confirmed_name:
        print("\nOperation cancelled.")
        sys.exit(0)
    
    # Get git repo and check status
    repo = get_git_repo()
    if not check_working_directory_clean(repo):
        print("\nOperation cancelled.")
        sys.exit(0)
    
    # Create/checkout branch
    handle_branch_creation(repo, confirmed_name)
    
    # Print summary and point to config.json
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"   Ticket: {selected_ticket.key}")
    print(f"   Summary: {selected_ticket.fields.summary}")
    print(f"   Type: {selected_ticket.fields.issuetype.name}")
    print(f"   Status: {selected_ticket.fields.status.name}")
    print(f"   Branch: {confirmed_name}")
    print("=" * 50)
    print("\nYou can manually edit the configuration at any time:")
    print(f"   {CONDUCTOR_HOME / 'config.json'}")


if __name__ == "__main__":
    main()
