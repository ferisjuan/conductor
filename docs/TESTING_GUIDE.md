# Conductor Testing Guide

Follow these steps to test all the changes made to Conductor.

## Prerequisites

Before testing, ensure you have:

- Python 3.10+ installed
- Git installed
- Internet connection (for Jira API and update checks)

## 🧪 Test Plan

### Phase 1: Basic Functionality Tests

#### Test 1: Help System

```bash
# Test help command (short form)
uv run conductor.py -h

# Test help command (long form)
uv run conductor.py --help

# Test with no arguments (should show help)
uv run conductor.py
```

**Expected Results:**

- Should display comprehensive help message
- Should show all commands: --setup, -b/--branch, --update, -h/--help
- Should include examples and getting started guide
- Should show configuration location (~/.conductor/)

---

#### Test 2: Import Validation

```bash
# Test that all imports work
uv run -c "import conductor; conductor.main()"

# Test individual module imports
uv run -c "import cli_help; print(cli_help.DESCRIPTION)"
uv run -c "import setup; print('Setup module loaded')"
uv run -c "import jira_branch_creator; print('Branch creator loaded')"
uv run -c "import conductor_setup; print('Update module loaded')"
uv run -c "import version; print('Version:', version.__version__)"
```

**Expected Results:**

- All imports should succeed without errors
- Should display help when running conductor.main()
- Each module should load successfully

---

### Phase 2: Setup Command Tests

#### Test 3: Initial Setup (Without Existing Config)

```bash
# Remove any existing config
rm -rf ~/.conductor/

# Run setup
uv run conductor.py --setup
```

**Follow the prompts:**

1. Enter company name (Atlassian subdomain)
2. Enter your Jira email
3. Enter your Jira API token
4. Select projects (optional)
5. Select statuses (optional)
6. Choose branch prefix preference

**Expected Results:**

- Should create ~/.conductor/ directory
- Should create ~/.conductor/config.json
- Should create ~/.conductor/.env with API token
- .env should have 600 permissions (on Unix)
- Should successfully connect to Jira
- Should fetch projects and statuses
- Should save configuration

**Verify:**

```bash
# Check directory exists
ls -la ~/.conductor/

# Check config file
cat ~/.conductor/config.json

# Check .env file (should show but be masked)
ls -l ~/.conductor/.env

# Verify permissions (should be -rw-------)
stat -f "%A" ~/.conductor/.env  # macOS
# or
stat -c "%a" ~/.conductor/.env  # Linux
```

---

#### Test 4: Reconfigure (With Existing Config)

```bash
# Run setup again
uv run conductor.py --setup
```

**Expected Results:**

- Should detect existing config
- Should offer to reuse existing values
- Should allow updating individual fields
- Should preserve unchanged values

---

### Phase 3: Branch Creation Tests

#### Test 5: Branch Creation (Short Flag)

```bash
# Navigate to a git repository first
cd /path/to/your/git/repo

# Run branch creation
uv run /Users/juan/wsp/conductor/conductor.py -b
```

**Expected Results:**

- Should fetch your Jira tickets from current sprint
- Should display tickets with status icons
- Should allow ticket selection
- Should generate branch name based on config
- Should create and checkout new branch

**Verify:**

```bash
# Check current branch
git branch --show-current

# Should show the newly created branch
```

---

#### Test 6: Branch Creation (Long Flag)

```bash
# Test with long form flag
uv run /Users/juan/wsp/conductor/conductor.py --branch
```

**Expected Results:**

- Should work identically to `-b` flag
- All same functionality as Test 5

---

### Phase 4: Update Command Tests

#### Test 7: Update Check

```bash
# Run update command
uv run conductor.py --update
```

**Expected Results:**

- Should check current version (from version.py)
- Should fetch latest version from GitHub
- Should compare versions
- If up to date: Display "You're already running the latest version!"
- If update available: Show update available message and prompt
- Should detect installation method (pip/uv/git/script)

---

### Phase 5: Config File Location Tests

#### Test 8: Verify Config Location

```bash
# Check that config is in home directory
ls -la ~/.conductor/

# Should see:
# - config.json
# - .env
# - .version_cache (after running conductor once)
```

**Expected Results:**

- All config files should be in ~/.conductor/
- Should NOT be in the conductor installation directory
- .env should have restricted permissions

---

### Phase 6: Edge Cases and Error Handling

#### Test 9: Missing Config Error

```bash
# Remove config
rm -rf ~/.conductor/

# Try to create branch without setup
uv run conductor.py -b
```

**Expected Results:**

- Should show error: "Error: config.json not found!"
- Should tell user to run: "Please run 'conductor --setup'"
- Should exit gracefully

---

#### Test 10: Invalid Config

```bash
# Create invalid JSON in config
echo "invalid json{{{" > ~/.conductor/config.json

# Try to run
uv run conductor.py -b
```

**Expected Results:**

- Should show JSON decode error
- Should exit gracefully
- Should not crash

---

### Phase 7: Integration Tests

#### Test 11: Full Workflow Test

```bash
# 1. Clean slate
rm -rf ~/.conductor/

# 2. Initial setup
uv run conductor.py --setup
# Complete all setup steps

# 3. View help
uv run conductor.py -h

# 4. Create a branch
cd /path/to/git/repo
uv run /Users/juan/wsp/conductor/conductor.py -b
# Select a ticket and create branch

# 5. Check for updates
uv run /Users/juan/wsp/conductor/conductor.py --update

# 6. Verify config location
ls -la ~/.conductor/
cat ~/.conductor/config.json
```

**Expected Results:**

- Complete workflow should work end-to-end
- All files should be in ~/.conductor/
- No errors at any step

---

## 🔍 Verification Checklist

After running all tests, verify:

- [ ] Help system works (-h, --help, no args)
- [ ] All imports succeed
- [ ] Setup creates ~/.conductor/ directory
- [ ] Setup creates config.json with correct structure
- [ ] Setup creates .env with API token
- [ ] .env has 600 permissions
- [ ] Setup connects to Jira successfully
- [ ] Reconfigure preserves existing values
- [ ] Branch creation with -b works
- [ ] Branch creation with --branch works
- [ ] Branches are created with correct naming
- [ ] Update check works
- [ ] Error handling works (missing config)
- [ ] Error handling works (invalid config)
- [ ] Config location is always ~/.conductor/

---

## 🐛 Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:** Install dependencies:

```bash
pip install jira gitpython python-dotenv questionary requests
```

### Issue: "conductor.py: No such file or directory"

**Solution:** Use full path:

```bash
uv run /Users/juan/wsp/conductor/conductor.py --help
```

### Issue: "Permission denied: ~/.conductor/.env"

**Solution:** Check file permissions:

```bash
chmod 600 ~/.conductor/.env
```

### Issue: "Can't connect to Jira"

**Solution:** Verify:

- Jira URL is correct
- Email is your full Jira email address
- API token is valid and not expired
- Get token from: <https://id.atlassian.com/manage-profile/security/api-tokens>

---

## 📊 Test Results Template

Use this template to track your test results:

```
Test 1 (Help -h):          [ PASS / FAIL ]
Test 2 (Imports):          [ PASS / FAIL ]
Test 3 (Initial Setup):    [ PASS / FAIL ]
Test 4 (Reconfigure):      [ PASS / FAIL ]
Test 5 (Branch -b):        [ PASS / FAIL ]
Test 6 (Branch --branch):  [ PASS / FAIL ]
Test 7 (Update):           [ PASS / FAIL ]
Test 8 (Config Location):  [ PASS / FAIL ]
Test 9 (Missing Config):   [ PASS / FAIL ]
Test 10 (Invalid Config):  [ PASS / FAIL ]
Test 11 (Full Workflow):   [ PASS / FAIL ]
```

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. Commit the changes
2. Update version in pyproject.toml and version.py
3. Create a git tag
4. Push to GitHub
5. Test installation from GitHub

---

## 📝 Notes

- Keep track of any errors or unexpected behavior
- Test on different operating systems if possible (macOS, Linux, Windows)
- Test with different Python versions (3.10, 3.11, 3.12+)
- Test with and without existing config files
