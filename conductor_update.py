#!/usr/bin/env python3
"""
Conductor Updater

Downloads and runs the latest version of the installer script.
"""

import os
import sys
import subprocess


def main():
    """Main update function."""
    print("Updating Conductor...")
    
    # URL of the raw installer script on GitHub
    installer_url = "https://raw.githubusercontent.com/ferisjuan/conductor/main/install.sh"
    
    # Path to temporarily store the installer
    temp_installer_path = "/tmp/conductor_install.sh"
    
    try:
        # Download the latest installer
        print(f"Downloading latest installer from {installer_url}...")
        subprocess.run(
            ["curl", "-fsSL", installer_url, "-o", temp_installer_path],
            check=True
        )
        
        # Make the installer executable
        os.chmod(temp_installer_path, 0o755)
        
        # Run the installer
        print("Running installer...")
        subprocess.run([temp_installer_path], check=True)
        
        print("\n✅ Conductor has been updated successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Update failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # Clean up the temporary installer
        if os.path.exists(temp_installer_path):
            os.remove(temp_installer_path)


if __name__ == "__main__":
    main()
