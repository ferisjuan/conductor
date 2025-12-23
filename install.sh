#!/bin/bash
# Conductor Installer
# Install with: curl -fsSL https://raw.githubusercontent.com/ferisjuan/conductor/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/ferisjuan/conductor"
RAW_URL="https://raw.githubusercontent.com/ferisjuan/conductor/main"
INSTALL_DIR="$HOME/.conductor"
BIN_DIR="$HOME/.local/bin"

# Print colored output
print_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

# Check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
  case "$(uname -s)" in
  Linux*) echo "linux" ;;
  Darwin*) echo "macos" ;;
  CYGWIN*) echo "windows" ;;
  MINGW*) echo "windows" ;;
  *) echo "unknown" ;;
  esac
}

# Check if uv is installed
check_uv() {
  if command_exists uv; then
    print_success "uv found"
    return 0
  fi
  return 1
}

# Install uv
install_uv() {
  print_info "Installing uv..."

  if ! curl -LsSf https://astral.sh/uv/install.sh | sh; then
    print_error "Failed to install uv"
    return 1
  fi

  # Add uv to PATH for current session
  export PATH="$HOME/.cargo/bin:$PATH"

  if command_exists uv; then
    print_success "uv installed successfully"
    return 0
  else
    print_error "uv installation failed"
    return 1
  fi
}

# Check Python installation
check_python() {
  local required_major=3
  local required_minor=14

  if command_exists python3; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
  elif command_exists python; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
  else
    return 1
  fi

  # Parse version
  MAJOR_VERSION=$(echo "$PYTHON_VERSION" | cut -d. -f1)
  MINOR_VERSION=$(echo "$PYTHON_VERSION" | cut -d. -f2)

  # Check if version meets requirements (3.8+)
  if [ "$MAJOR_VERSION" -eq "$required_major" ] && [ "$MINOR_VERSION" -ge "$required_minor" ]; then
    return 0
  elif [ "$MAJOR_VERSION" -gt "$required_major" ]; then
    return 0
  fi

  return 1
}

# Install via uv
install_via_uv() {
  print_info "Installing Conductor via uv..."

  # Try installing from GitHub
  if uv pip install "git+${REPO_URL}.git" --system 2>&1 | grep -v "Requirement already satisfied" || true; then
    print_success "Conductor installed via uv"
    return 0
  else
    print_error "Failed to install via uv"
    return 1
  fi
}

# Install via script (fallback)
install_via_script() {
  print_info "Installing Conductor via direct download..."

  # Create installation directory
  mkdir -p "$INSTALL_DIR"

  # Download main files
  print_info "Downloading files..."
  curl -fsSL "$RAW_URL/conductor.py" -o "$INSTALL_DIR/conductor.py"
  curl -fsSL "$RAW_URL/setup.py" -o "$INSTALL_DIR/setup.py"
  curl -fsSL "$RAW_URL/version.py" -o "$INSTALL_DIR/version.py"
  curl -fsSL "$RAW_URL/update.py" -o "$INSTALL_DIR/update.py"

  # Make scripts executable
  chmod +x "$INSTALL_DIR/conductor.py"
  chmod +x "$INSTALL_DIR/setup.py"
  chmod +x "$INSTALL_DIR/update.py"

  # Install Python dependencies
  print_info "Installing dependencies..."
  if command_exists uv; then
    uv pip install jira questionary gitpython python-dotenv requests --system
  elif command_exists pip3; then
    pip3 install --user jira questionary gitpython python-dotenv requests
  elif command_exists pip; then
    pip install --user jira questionary gitpython python-dotenv requests
  else
    print_error "No package manager found (pip/uv)"
    return 1
  fi

  print_success "Files installed to $INSTALL_DIR"
  return 0
}

# Create wrapper scripts
create_wrappers() {
  print_info "Creating command shortcuts..."

  # Create bin directory if it doesn't exist
  mkdir -p "$BIN_DIR"

  # Detect if installed via uv or script
  if command_exists uv && uv pip show conductor >/dev/null 2>&1; then
    # Create wrappers that use the uv-installed package
    cat >"$BIN_DIR/conductor" <<'EOF'
#!/bin/bash
python3 -m conductor "$@"
EOF

    cat >"$BIN_DIR/conductor-setup" <<'EOF'
#!/bin/bash
python3 -m setup "$@"
EOF

    cat >"$BIN_DIR/conductor-update" <<'EOF'
#!/bin/bash
python3 -m update "$@"
EOF
  else
    # Create wrappers for script installation
    cat >"$BIN_DIR/conductor" <<EOF
#!/bin/bash
$PYTHON_CMD "$INSTALL_DIR/conductor.py" "\$@"
EOF

    cat >"$BIN_DIR/conductor-setup" <<EOF
#!/bin/bash
$PYTHON_CMD "$INSTALL_DIR/setup.py" "\$@"
EOF

    cat >"$BIN_DIR/conductor-update" <<EOF
#!/bin/bash
$PYTHON_CMD "$INSTALL_DIR/update.py" "\$@"
EOF
  fi

  # Make wrappers executable
  chmod +x "$BIN_DIR/conductor"
  chmod +x "$BIN_DIR/conductor-setup"
  chmod +x "$BIN_DIR/conductor-update"

  print_success "Commands created: conductor, conductor-setup, conductor-update"
}

# Check if directory is in PATH
check_path() {
  if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    print_warning "$BIN_DIR is not in your PATH"

    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    case "$SHELL_NAME" in
    bash)
      SHELL_RC="$HOME/.bashrc"
      ;;
    zsh)
      SHELL_RC="$HOME/.zshrc"
      ;;
    fish)
      SHELL_RC="$HOME/.config/fish/config.fish"
      ;;
    *)
      SHELL_RC="$HOME/.profile"
      ;;
    esac

    echo ""
    print_info "Add this line to your $SHELL_RC:"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    print_info "Then reload your shell with: source $SHELL_RC"
    echo ""
  fi
}

# Main installation
main() {
  echo ""
  echo "╔════════════════════════════════════════════╗"
  echo "║         Conductor Installer                ║"
  echo "║   Jira Ticket Branch Creator               ║"
  echo "╚════════════════════════════════════════════╝"
  echo ""

  OS=$(detect_os)
  print_info "Detected OS: $OS"

  # Check Python
  if ! check_python; then
    print_error "Python 3.14+ is not installed"
    print_info "Please install Python 3.14 or higher (tested with Python 3.14):"
    echo ""
    case "$OS" in
    macos)
      echo "    brew install python@3.14"
      echo "    # or"
      echo "    brew install python3"
      ;;
    linux)
      echo "    sudo apt install python3 python3-pip  # Debian/Ubuntu"
      echo "    sudo yum install python3 python3-pip  # RHEL/CentOS"
      echo "    # or use pyenv to install Python 3.14"
      ;;
    esac
    echo ""
    exit 1
  fi

  print_success "Python found: $PYTHON_CMD (version $PYTHON_VERSION)"

  # Check/Install uv
  if ! check_uv; then
    print_warning "uv not found"
    read -p "$(echo -e ${BLUE}?${NC}) Install uv (recommended package manager)? [Y/n]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
      if ! install_uv; then
        print_warning "Continuing with pip installation..."
      fi
    fi
  fi

  # Try installation via uv first, fall back to script
  if command_exists uv; then
    if install_via_uv; then
      INSTALL_METHOD="uv"
    else
      print_warning "Falling back to script installation..."
      install_via_script
      INSTALL_METHOD="script"
    fi
  else
    install_via_script
    INSTALL_METHOD="script"
  fi

  # Create wrapper scripts
  create_wrappers

  # Check PATH
  check_path

  echo ""
  echo "╔════════════════════════════════════════════╗"
  echo "║  ✓ Installation Complete!                 ║"
  echo "╚════════════════════════════════════════════╝"
  echo ""
  print_success "Conductor installed successfully!"
  print_info "Installation method: $INSTALL_METHOD"
  echo ""
  print_info "Next steps:"
  echo "  1. Run 'conductor-setup' to configure your Jira credentials"
  echo "  2. Navigate to any git repository"
  echo "  3. Run 'conductor' to create branches from Jira tickets"
  echo ""
  print_info "Update anytime with: conductor-update"
  echo ""
}

# Run main installation
main
