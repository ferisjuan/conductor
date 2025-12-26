# 🎯 Conductor

> Jira Ticket Branch Creator - Streamline your git workflow

Conductor fetches your Jira tickets and creates git branches with a single command. No more manually typing branch names or looking up ticket numbers.

## ✨ Features

- 🎫 Fetches tickets assigned to you in the current sprint
- 🌿 Creates properly formatted git branches
- 🔍 Filters by project and status
- 📊 Shows ticket status with visual indicators
- ⚙️ Highly configurable branch naming patterns
- 🔒 Secure credential storage

## 🚀 Quick Install

Install Conductor with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/ferisjuan/conductor/main/install.sh | bash
```

The installer will:

- ✅ Check for Python 3.10+
- ✅ Optionally install `uv` (recommended modern package manager)
- ✅ Install Conductor and dependencies
- ✅ Create command shortcuts (`conductor`, `conductor --setup`, `conductor --update`)
- ✅ Set up automatic update checking

### Alternative Installation Methods

**Using uv (recommended):**

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Conductor
uv pip install git+https://github.com/ferisjuan/conductor.git --system
```

**Using pip:**

```bash
pip install git+https://github.com/ferisjuan/conductor.git
```

**Manual installation:**

```bash
git clone https://github.com/ferisjuan/conductor.git
cd conductor
uv pip install -e . --system  # or: pip install -e .
```

## 🔄 Updating

Conductor automatically checks for updates once per day. When an update is available, you'll see:

```
============================================================
🎉 New version available: v1.1.0 (current: v1.0.0)
============================================================

📦 Update with:
   conductor --update
============================================================
```

### Update Commands

```bash
# Update to latest version
conductor --update

# Check current version
conductor --version

# Force check for updates
python -m version --check
```

## 📋 Requirements

- Python 3.10+ (tested with Python 3.14)
- Git
- Jira account with API access

## 🎬 Getting Started

### 1. Initial Setup

Run the setup wizard to configure your Jira credentials:

```bash
conductor --setup
```

This will:

- Connect to your Jira instance
- Fetch available projects and statuses
- Configure branch naming preferences
- Store credentials securely

### 2. Create Branches

Navigate to any git repository and run:

```bash
conductor -b
# or
conductor --branch
```

This will:

- Show your assigned tickets in the current sprint
- Let you select a ticket
- Create and checkout a new branch

## 🎨 Example Output

```
Conductor - Jira Ticket Branch Creator
==================================================

🔍 Using JQL: assignee = 'your.email@company.com' AND sprint in openSprints()
✅ Found 12 ticket(s)

Select a ticket to create a branch for:
  1. 🔨 CDEM-1234 - Implement user authentication [In Progress]
  2. 📋 CDEM-1235 - Add dashboard widgets [Ready for Work]
  3. 👀 CDEM-1236 - Fix payment validation [Peer Review]
  4. 🧪 CDEM-1237 - Update API documentation [Ready for QA]
  5. 🎯 CDEM-1238 - Refactor search logic [UAT]

Generated branch name: feature/CDEM-1234-implement-user-authentication
Branch prefixes are ✅ enabled (change in config.json if needed)

✓ Created and checked out new branch: feature/CDEM-1234-implement-user-authentication
```

## ⚙️ Configuration

After setup, you can edit `~/.conductor-devtools/config.json`:

```json
{
  "jira_server": "https://your-company.atlassian.net",
  "jira_username": "your.email@company.com",
  "project_keys": ["CDEM", "PROJ"],
  "ticket_statuses": ["Ready For Work", "Working", "Ready for QA"],
  "use_branch_prefixes": true,
  "ticket_code_case": "lower",
  "branch_pattern": "{type}/{ticket_key}-{summary}",
  "max_results": 100,
  "branch_prefixes": {
    "Bug": "bugfix",
    "Story": "feature",
    "Task": "feature",
    "Epic": "feature",
    "Improvement": "improvement",
    "Spike": "spike"
  }
}
```

### Branch Naming Options

**With prefixes enabled:**

```
feature/CDEM-1234-implement-user-authentication
bugfix/CDEM-5678-fix-login-error
improvement/CDEM-9012-optimize-queries
```

**With prefixes disabled:**

```
CDEM-1234-implement-user-authentication
CDEM-5678-fix-login-error
CDEM-9012-optimize-queries
```

### Status Icons

- 🔨 In Progress / Working
- 📋 Ready for Work / To Do
- 👀 Peer Review / Code Review
- 🧪 Ready for QA / Testing
- 🎯 UAT / User Acceptance
- ✅ Done / Completed
- 🚫 Blocked
- ⏸️ On Hold
- ⏳ Waiting

## 🔐 Security

- API tokens are stored in `~/.conductor-devtools/.env` with restricted permissions (600)
- Never commit `.env` files to version control
- Generate API tokens at: <https://id.atlassian.com/manage-profile/security/api-tokens>

## 🛠️ Commands

- `conductor -b` or `conductor --branch` - Create a branch from a Jira ticket
- `conductor --setup` - Run the setup wizard (initial config or updates)
- `conductor --update` - Check for updates and install the latest version
- `conductor -h` or `conductor --help` - Show help message

## 📁 File Locations

- Installation: `~/.conductor-devtools/`
- Configuration: `~/.conductor-devtools/config.json`
- Credentials: `~/.conductor-devtools/.env`
- Commands: `~/.local/bin/conductor`, `~/.local/bin/conductor-setup`

## 🐛 Troubleshooting

### "conductor: command not found"

Add `~/.local/bin` to your PATH:

```bash
# For bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### "No tickets found"

- Check that you're assigned tickets in an active sprint
- Remove project/status filters in `config.json` to see all tickets
- Verify your Jira credentials are correct

### Connection Issues

- Ensure your API token hasn't expired
- Verify your email address is correct (must be full email)
- Check your company's Jira URL

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Credits

Created by Juan Feris. [Buy me a coffee](https://buymeacoffee.com/ferisjuan)

---

**Need help?** Open an issue on GitHub or run `conductor --setup` to reconfigure.
