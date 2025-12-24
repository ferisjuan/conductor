## [v1.0.2] - 2025-12-24

## [v1.0.1] - 2025-12-23

## [v1.0.0] - 2025-12-23

# Changelog

All notable changes to Conductor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.0] - 2025-12-23

### Added

- Initial release
- Jira ticket fetching from current sprint
- Automatic git branch creation
- Configurable branch naming patterns
- Status icons for visual ticket identification
- Support for branch prefixes (feature/, bugfix/, etc.)
- Secure credential storage
- Interactive setup wizard
- Automatic update checking
- `uv` package manager support
- `conductor-update` command for easy updates
- Project and status filtering
- Customizable branch patterns

### Features

- 🎫 Fetches tickets assigned to you in current sprint
- 🌿 Creates properly formatted git branches
- 🔍 Filters by project and status
- 📊 Shows ticket status with visual indicators (🔨 🧪 ✅ etc.)
- ⚙️ Highly configurable via config.json
- 🔒 Secure credential storage (.env with 600 permissions)
- 🔄 Automatic update notifications
- 📦 Multiple installation methods (curl, uv, pip)

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

[v1.0.0]: https://github.com/ferisjuan/conductor/releases/tag/v1.0.0
