#!/usr/bin/env python3
"""
Conductor Setup

Interactive setup that configures Jira credentials and fetches project/status options.
Writes data incrementally to avoid losing progress on failures.
"""

import json
import os
import sys
from pathlib import Path

import questionary
from jira import JIRA

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
CONFIG_EXAMPLE = SCRIPT_DIR / "config.example.json"
ENV_PATH = SCRIPT_DIR / ".env"


def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    
    try:
        import questionary
    except ImportError:
        missing.append("questionary")
    
    try:
        import jira
    except ImportError:
        missing.append("jira")
    
    try:
        import git
    except ImportError:
        missing.append("GitPython")
    
    if missing:
        print("Error: Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing)}")
        sys.exit(1)


def load_existing_config():
    """Load existing config if available."""
    config = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            print(f"Found existing config: {CONFIG_PATH}")
        except json.JSONDecodeError:
            print(f"Warning: Could not read existing config, starting fresh")
    return config


def load_existing_env():
    """Load existing .env if available."""
    api_token = None
    if ENV_PATH.exists():
        try:
            with open(ENV_PATH, 'r') as f:
                for line in f:
                    if line.startswith('JIRA_API_TOKEN='):
                        api_token = line.strip().split('=', 1)[1]
                        break
            if api_token:
                print(f"Found existing API token: {ENV_PATH}")
        except Exception as e:
            print(f"Warning: Could not read existing .env: {e}")
    return api_token


def prompt_for_credentials(existing_config=None, existing_token=None):
    """Prompt user for Jira credentials with option to reuse existing."""
    print("Conductor Setup")
    print("=" * 50)
    
    config = existing_config or {}
    
    # Company name
    company_name = config.get("jira_server", "").replace("https://", "").replace(".atlassian.net", "")
    if company_name and questionary.confirm(f"Use existing company '{company_name}'?", default=True).ask():
        jira_server = f"https://{company_name}.atlassian.net"
    else:
        company_name = questionary.text(
            "Enter your company name (e.g., 'your-company'):",
            validate=lambda text: len(text.strip()) > 0 or "Company name cannot be empty"
        ).ask()
        if not company_name:
            print("Setup cancelled.")
            sys.exit(0)
        jira_server = f"https://{company_name}.atlassian.net"
    
    # Username (email)
    username = config.get("jira_username")
    if username and questionary.confirm(f"Use existing username '{username}'?", default=True).ask():
        pass
    else:
        username = questionary.text(
            "Enter your Jira EMAIL (full address like name@company.com):",
            validate=lambda text: ('@' in text and len(text.strip()) > 0) or "Must be a valid email address"
        ).ask()
        if not username:
            print("Setup cancelled.")
            sys.exit(0)
    
    # API token
    api_token = existing_token
    if api_token and questionary.confirm(f"Use existing API token (masked)?", default=True).ask():
        pass
    else:
        print("\nGet API token from: https://id.atlassian.com/manage-profile/security/api-tokens")
        api_token = questionary.password(
            "Enter your Jira API token:",
            validate=lambda text: len(text.strip()) > 0 or "Token cannot be empty"
        ).ask()
        if not api_token:
            print("Setup cancelled.")
            sys.exit(0)
    
    return jira_server, username, api_token


def test_jira_connection(server: str, username: str, api_token: str):
    """Test Jira connection and return JIRA client."""
    if '@' not in username:
        print(f"ERROR: Username '{username}' must be a full email address!")
        print("Example: juan.feris@invitationhomes.com")
        sys.exit(1)
    
    try:
        jira = JIRA(server=server, basic_auth=(username, api_token))
        jira.myself()  # Test connection
        print("✅ Successfully connected to Jira")
        return jira
    except Exception as e:
        # Safe error printing (handles encoding issues)
        try:
            error_msg = str(e)
        except UnicodeEncodeError:
            error_msg = "Authentication failed - check credentials"
        
        print(f"❌ Error connecting to Jira: {error_msg}")
        print("\nPlease verify:")
        print("  - Email is your FULL Jira email address")
        print("  - API token is valid and not expired")
        print("  - Company name is correct")
        sys.exit(1)


def fetch_projects(jira: JIRA):
    """Fetch available Jira projects."""
    try:
        projects = jira.projects()
        if not projects:
            print("No projects found or insufficient permissions.")
            return []
        
        projects_sorted = sorted(projects, key=lambda p: p.key)
        print(f"Found {len(projects_sorted)} project(s)")
        return projects_sorted
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []


def fetch_statuses(jira: JIRA):
    """Fetch available Jira statuses."""
    try:
        statuses = jira.statuses()
        if not statuses:
            print("No statuses found or insufficient permissions.")
            return []
        
        status_names = sorted(set(status.name for status in statuses))
        print(f"Found {len(status_names)} status(es)")
        return status_names
    except Exception as e:
        print(f"Error fetching statuses: {e}")
        return []


def select_projects(projects, existing_projects=None):
    """Let user select one or more projects (optional)."""
    if not projects:
        return existing_projects or []
    
    # Pre-select existing choices if available
    choices = [
        questionary.Choice(title=f"{p.key} - {p.name}", value=p.key, checked=(existing_projects and p.key in existing_projects))
        for p in projects
    ]
    
    selected = questionary.checkbox(
        "Select project keys to include (Space to select, Enter to confirm, optional):",
        choices=choices,
        instruction="Use Space to select/deselect, Enter to confirm (can be empty)"
    ).ask()
    
    return selected if selected is not None else []


def select_statuses(statuses, existing_statuses=None):
    """Let user select one or more statuses (optional)."""
    if not statuses:
        return existing_statuses or []
    
    # Pre-select existing choices if available
    choices = [
        questionary.Choice(title=s, value=s, checked=(existing_statuses and s in existing_statuses))
        for s in statuses
    ]
    
    selected = questionary.checkbox(
        "Select ticket statuses to include (Space to select, Enter to confirm, optional):",
        choices=choices,
        instruction="Use Space to select/deselect, Enter to confirm (can be empty)"
    ).ask()
    
    return selected if selected is not None else []


def ask_branch_prefixes(existing_config=None):
    """Ask user if they want to use branch prefixes with examples."""
    print("\n" + "=" * 50)
    print("Branch Prefix Configuration")
    print("=" * 50)
    print("\n✅ With prefixes enabled:")
    print("  - Bug:         bugfix/CDEM-123-fix-login-error")
    print("  - Story:       feature/CDEM-456-user-dashboard")
    print("  - Task:        feature/CDEM-789-update-docs")
    print("  - Epic:        feature/CDEM-101-roadmap-item")
    print("  - Improvement: improvement/CDEM-202-refactor-api")
    print("  - Spike:       spike/CDEM-303-research-solution")
    print("\n❌ Without prefixes:")
    print("  - Bug:         CDEM-123-fix-login-error")
    print("  - Story:       CDEM-456-user-dashboard")
    print("  - Task:        CDEM-789-update-docs")
    print("  - Epic:        CDEM-101-roadmap-item")
    print("  - Improvement: CDEM-202-refactor-api")
    print("  - Spike:       CDEM-303-research-solution")
    print()
    
    # Get existing preference if available
    default_value = True
    if existing_config and "use_branch_prefixes" in existing_config:
        default_value = existing_config["use_branch_prefixes"]
    
    use_prefixes = questionary.confirm(
        "Use branch prefixes (recommended for clarity)?",
        default=default_value
    ).ask()
    
    if use_prefixes is None:
        print("Setup cancelled.")
        sys.exit(0)
    
    return use_prefixes


def save_config_partial(config_data):
    """Save config data incrementally."""
    try:
        # Load existing config if any
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update with new data
        config.update(config_data)
        
        # Save back to file
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Saved to {CONFIG_PATH}")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False


def save_env_file(api_token):
    """Create .env file with API token."""
    try:
        with open(ENV_PATH, 'w') as f:
            f.write(f"JIRA_API_TOKEN={api_token}\n")
        
        # Set file permissions to be readable only by owner (security best practice)
        if os.name != 'nt':  # Unix-like systems
            ENV_PATH.chmod(0o600)
        
        print(f"💾 Created {ENV_PATH} (permissions: 600)")
        return True
    except Exception as e:
        print(f"❌ Error creating {ENV_PATH}: {e}")
        return False


def main():
    """Main setup function."""
    print("Conductor Setup")
    print("This will configure your Jira credentials and fetch project settings.\n")
    
    # Check dependencies first
    check_dependencies()
    
    # Load existing data if available
    existing_config = load_existing_config()
    existing_token = load_existing_env()
    
    # Prompt for credentials (with option to reuse)
    server, username, api_token = prompt_for_credentials(existing_config, existing_token)
    
    # Save credentials immediately
    print("\n💾 Saving credentials...")
    save_config_partial({
        "jira_server": server,
        "jira_username": username
    })
    save_env_file(api_token)
    
    # Test connection and get Jira client
    print("\n🔄 Testing connection...")
    jira = test_jira_connection(server, username, api_token)
    
    # Fetch and select projects (optional)
    print("\n🔄 Fetching available projects...")
    projects = fetch_projects(jira)
    existing_projects = existing_config.get("project_keys", [])
    selected_projects = select_projects(projects, existing_projects)
    
    # Save projects immediately
    if selected_projects is not None:
        print("\n💾 Saving projects...")
        save_config_partial({"project_keys": selected_projects})
    
    # Fetch and select statuses (optional)
    print("\n🔄 Fetching available statuses...")
    statuses = fetch_statuses(jira)
    existing_statuses = existing_config.get("ticket_statuses", [])
    selected_statuses = select_statuses(statuses, existing_statuses)
    
    # Save statuses immediately
    if selected_statuses is not None:
        print("\n💾 Saving statuses...")
        save_config_partial({"ticket_statuses": selected_statuses})
    
    # Ask about branch prefixes (now in setup)
    use_branch_prefixes = ask_branch_prefixes(existing_config)
    save_config_partial({"use_branch_prefixes": use_branch_prefixes})
    
    # Set defaults for other fields if not present
    print("\n🔧 Finalizing configuration...")
    final_config = {
        "branch_pattern": "{type}/{ticket_key}-{summary}",
        "max_results": 100,
        "additional_jql": "",
        "ticket_code_case": "lower",
        "branch_prefixes": {
            "Bug": "bugfix",
            "Story": "feature",
            "Task": "feature",
            "Epic": "feature",
            "Improvement": "improvement",
            "Spike": "spike"
        }
    }
    
    # Only add defaults if they don't exist
    config_to_save = {}
    for key, value in final_config.items():
        if key not in existing_config:
            config_to_save[key] = value
    
    if config_to_save:
        save_config_partial(config_to_save)
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print(f"   Server:           {server}")
    print(f"   Username:         {username}")
    print(f"   Projects:         {', '.join(selected_projects) if selected_projects else 'All projects'}")
    print(f"   Statuses:         {', '.join(selected_statuses) if selected_statuses else 'All statuses'}")
    print(f"   Branch prefixes:  {'✅ Enabled' if use_branch_prefixes else '❌ Disabled'}")
    print(f"   Config file:      {CONFIG_PATH}")
    print(f"   Token file:       {ENV_PATH} (secure)")
    print("=" * 50)
    print("\n📝 You can edit the configuration at any time:")
    print(f"   {CONFIG_PATH.absolute()}")
    print("\n🚀 Next step: Run the branch creator from any git repository:")
    print("   python conductor.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
