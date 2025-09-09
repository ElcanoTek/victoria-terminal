# Victoria Script Testing

This repository includes comprehensive tests for the `victoria.py` starter script to ensure it works correctly across different platforms and terminal environments.

## Test Coverage

### Automated Testing (GitHub Actions)

The GitHub Actions workflow (`.github/workflows/test-victoria.yml`) automatically tests the script on:

- **Operating Systems**: Ubuntu (Linux), Windows, macOS
- **Python Version**: Latest stable Python (3.x)
- **Terminal Environments**: Various TERM settings, PowerShell (Windows), Bash (Unix)
- **Locale Settings**: UTF-8, C locale, and others

### Test Categories

1. **Import Tests**: Verifies all required Python modules are available
2. **Syntax Tests**: Ensures the script has valid Python syntax
3. **Terminal Capability Detection**: Tests cross-platform terminal feature detection
4. **Cross-Platform Compatibility**: Validates file operations and platform detection
5. **Environment Variable Handling**: Tests environment variable access and manipulation
6. **Script Execution**: Verifies the script runs without hanging in different environments
7. **Unicode Handling**: Tests emoji and Unicode character support
8. **JSON Operations**: Validates JSON parsing and file I/O operations

### Running Tests Locally

All test scripts now reside in the `tests/` directory. To run the full test suite:

```bash
pytest tests/test_victoria.py tests/test_non_interactive.py
```

Or run the scripts directly:

```bash
python tests/test_victoria.py
python tests/test_non_interactive.py
```

### Test Script Features

- **Cross-Platform**: Works on Windows, macOS, and Linux
- **No Dependencies**: Uses only Python standard library modules
- **Comprehensive Coverage**: Tests all major functionality without requiring external services
- **Graceful Degradation**: Tests that the script handles different terminal capabilities appropriately
- **Non-Destructive**: All tests clean up after themselves

### GitHub Actions Matrix

The CI pipeline tests multiple combinations:

- **Linux**: All Python versions (3.8-3.12)
- **Windows**: Python 3.10, 3.11, 3.12 (reduced matrix for efficiency)
- **macOS**: Python 3.10, 3.11, 3.12 (reduced matrix for efficiency)

### Terminal Environment Testing

The workflow specifically tests:

- No TERM variable set
- TERM=dumb (basic terminal)
- TERM=xterm-256color (full-featured terminal)
- Different shells (bash, PowerShell, CMD on Windows)
- Various locale settings (UTF-8, C locale)
- Debug mode enabled

### Expected Behavior

The `victoria.py` script is designed to:

- Display a fancy banner with Unicode characters and emojis when supported
- Gracefully degrade to ASCII alternatives on basic terminals
- Handle user interruption (Ctrl+C) gracefully
- Prompt for user input and handle different response scenarios
- Work without requiring external dependencies or network access for basic functionality

### Continuous Integration

Tests run automatically on:

- Every push to `main` or `develop` branches
- Every pull request to `main` or `develop` branches
- Manual workflow dispatch

All tests must pass before code can be merged, ensuring the script remains compatible across all supported platforms and environments.

---

## Manual Installer Testing with Vagrant and VirtualBox

For testing the final packaged installers (`VictoriaSetup.exe` and `.AppImage`), this project includes a Vagrant setup to quickly create and destroy clean virtual machines for Windows 11 and Ubuntu.

### Prerequisites

Before you begin, you must install the following software on your host machine:

1.  **VirtualBox**: [Download and install VirtualBox](https://www.virtualbox.org/wiki/Downloads).
2.  **Vagrant**: [Download and install Vagrant](https://www.vagrantup.com/downloads).

### Testing Workflow

Follow these steps to test an installer on a fresh OS.

**Step 1: Download the Installer**

Go to the project's **GitHub Releases** page or the **Actions** tab and download the installer artifact you wish to test (e.g., `VictoriaSetup.exe` or `Victoria-*.AppImage`).

**Step 2: Place the Installer in the Project Root**

Place the downloaded installer file into the main root directory of this repository. A placeholder file named `PUT_INSTALLER_HERE.txt` indicates the correct location. The provisioning scripts inside the VMs will look for the installer in this shared directory.

**Step 3: Launch the Virtual Machine**

Open a terminal in the project's root directory and run one of the following commands:

-   **To test on Windows 11:**
    ```bash
    vagrant up windows11
    ```

-   **To test on Ubuntu 22.04:**
    ```bash
    vagrant up ubuntu
    ```

**Note:** The first time you run this command for a specific OS, it will download the base virtual machine image, which can be several gigabytes. The Ubuntu VM will also take a significant amount of time to install its desktop environment. Subsequent launches will be much faster.

**Step 4: Test the Application**

A VirtualBox window will appear, booting the respective operating system. The provisioning process will handle the installation automatically.

-   **On Windows 11**: The script runs the installer silently in the background. Once the VM is ready, you can find **Victoria** in the Start Menu and launch it to begin testing.
-   **On Ubuntu**: The script places the AppImage on the `vagrant` user's desktop. Log in to the desktop (password is `vagrant`), and you will see the Victoria AppImage icon. Double-click it to run and begin testing.

**Step 5: Clean Up**

Once you have finished testing, you can completely remove the virtual machine and free up all associated disk space with the `destroy` command.

-   **To destroy the Windows VM:**
    ```bash
    vagrant destroy windows11 -f
    ```

-   **To destroy the Ubuntu VM:**
    ```bash
    vagrant destroy ubuntu -f
    ```

### Useful Vagrant Commands

-   **Re-run Provisioning**: If you change an installer file and want to re-run the installation without rebuilding the VM from scratch:
    ```bash
    vagrant reload --provision <vm_name>
    ```
-   **SSH Access**: To get a command-line shell inside a running VM:
    ```bash
    vagrant ssh <vm_name>
    ```
-   **Halt vs. Destroy**:
    - `vagrant halt`: Shuts down the VM but preserves its state on disk (like turning off a computer).
    - `vagrant destroy`: Completely removes the VM and all its data.