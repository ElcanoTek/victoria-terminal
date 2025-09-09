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

**Step 1: Place the Installer in the `installers/` Directory**

Go to the project's **GitHub Releases** page or the **Actions** tab and download the installer artifact you wish to test (e.g., `VictoriaSetup.exe` or `Victoria-*.AppImage`).

Place the downloaded installer file into the `installers/` directory in the root of this repository. The provisioning scripts inside the VMs are configured to look for the installer in this directory.

**Step 2: Launch the Virtual Machine**

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

**Step 3: Test the Application**

A VirtualBox window will appear, booting the respective operating system. The provisioning process will handle the installation automatically.

-   **On Windows 11**: The script runs the installer silently in the background. Once the VM is ready, you can find **Victoria** in the Start Menu and launch it to begin testing.
-   **On Ubuntu**: The script places the AppImage on the `vagrant` user's desktop. Log in to the desktop (password is `vagrant`), and you will see the Victoria AppImage icon. Double-click it to run and begin testing.

**Step 4: Clean Up**

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

---

## Manual Installer Testing with UTM on Apple Silicon

For users on Apple Silicon Macs, this project provides a semi-automated way to test the macOS installer using [UTM](https://mac.getutm.app/). This approach uses a script to manage a temporary test VM, but requires some manual steps inside the VM.

### Prerequisites

1.  **UTM**: [Download and install UTM](https://mac.getutm.app/) from the official website.
2.  **`utmctl`**: The `run_utm_test.sh` script uses `utmctl`, UTM's command-line tool. You should make it accessible from your `PATH`. A common way to do this is to create a symbolic link:
    ```bash
    sudo ln -sf /Applications/UTM.app/Contents/MacOS/utmctl /usr/local/bin/utmctl
    ```

### One-Time Setup: Create a Base VM

Before you can run a test, you need to create a "base" macOS virtual machine. This VM will serve as a clean template for testing.

1.  **Install macOS**: Create a new macOS VM in UTM. Apple provides official IPSW files for Apple Silicon that can be used for this.
2.  **Name the VM**: Name the VM exactly `macOS Base`. The control script looks for this name.
3.  **Configure a Shared Directory**: In the VM's settings, go to the "Sharing" tab and enable "Directory Sharing". Choose a directory on your host machine that will be used to share files with the VM. Inside the guest macOS, this directory will be mounted at `/Users/Shared`.
4.  **Install Dependencies**: Start the VM and install any necessary dependencies (e.g., `jq` if you plan to use the provisioning script).
5.  **Shut Down**: Once the base VM is set up, shut it down. Do not delete it.

### Testing Workflow

**Step 1: Place Files in Shared Directory**

1.  **Installer**: Download the macOS installer, `Victoria-*.app.zip`, from the GitHub Releases page. Place it in a subdirectory named `installers` inside your main shared directory.
2.  **Provisioning Script**: Find the `provision_macos.sh` script in the `tests/` directory of this repository. Place this script in your main shared directory (not the `installers` subdirectory).

**Step 2: Run the Test Script**

Open a terminal on your host Mac, navigate to the root of this project, and run:

```bash
bash tests/run_utm_test.sh
```

The script will:
1.  Clone the `macOS Base` VM to a new VM named `macOS Test`.
2.  Start the `macOS Test` VM.
3.  Pause and wait for you to perform manual testing.

**Step 3: Test the Application**

1.  **Open Terminal in VM**: Once the `macOS Test` VM has booted, open the Terminal application.
2.  **Run Provisioning Script**: Execute the provisioning script from the shared directory:
    ```bash
    bash /Users/Shared/provision_macos.sh
    ```
    This will find the installer in the `installers` subdirectory, unzip the application, and move `Victoria.app` to the `/Applications` folder.
3.  **Test**: Launch Victoria from the Applications folder and perform your tests.

**Step 4: Clean Up**

Once you are finished testing, return to the terminal on your host Mac where `run_utm_test.sh` is running and press `Enter`. The script will automatically stop and delete the `macOS Test` VM, freeing up all associated disk space.