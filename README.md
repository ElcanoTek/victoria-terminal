# Victoria

<img src="assets/icon.png" alt="Victoria Icon" width="200" />

Victoria is Elcano's AI agent that connects to programmatic advertising reports via MCP. Traders can ask powerful questions of CSVs, Excel files, and SQL-queryable datasets — making it easier to surface insights, spot trends, and optimize campaigns.

---

## ⚙️ Installation

### Dependencies

You may install prerequisites manually or run the platform script in the [dependencies](./dependencies) folder.

* `crush` – [GitHub](https://github.com/charmbracelet/crush)
* `uv` – [Docs](https://docs.astral.sh/uv/getting-started/installation/)
* `python` – download from [python.org](https://www.python.org) or use your platform's package manager.

## Python Packages (developers only)

The bundled application includes its own Python libraries. When running
`victoria.py` directly, install the UI helpers manually:

```bash
uv pip install colorama rich
```

Verify the installation:

```bash
python3 -c "import colorama, rich; print(colorama.__version__, rich.__version__)"
```

### Environment Variables

Set your environment variables manually or use `set_env_macos_linux.sh` or `set_env_windows.ps1` in the [dependencies](./dependencies) folder to configure these values.

* `OPENROUTER_API_KEY` (required)
* `SNOWFLAKE_ACCOUNT` (optional)
* `SNOWFLAKE_USER` (optional)
* `SNOWFLAKE_PASSWORD` (optional)
* `SNOWFLAKE_WAREHOUSE` (optional)
* `SNOWFLAKE_ROLE` (optional)

---

## 🚀 Launching Victoria

Open your terminal, change into the `victoria-app` folder, and run:

```bash
cd /path/to/victoria-app
python3 victoria.py
```

This gives you the most control and is the same across macOS, Linux, and Windows (PowerShell).
All modes store configuration and data in `~/Victoria` (or `%USERPROFILE%\Victoria` on Windows).

### Customizing the launch tool

Victoria uses the `crush` CLI by default. Set the following environment variables to swap in a different tool or config files:

```bash
export VICTORIA_TOOL="your_cli"
export VICTORIA_TEMPLATE="your_cli.template.json"
export VICTORIA_OUTPUT="your_cli.json"
```

## 🔄 On-Demand GitHub Actions

Two workflows in [`.github/workflows`](.github/workflows) can be run manually from the **Actions** tab or via the GitHub CLI.

* **Manual Tests** ([`manual-tests.yml`](.github/workflows/manual-tests.yml)) — runs `tests/test_victoria.py` and `tests/test_non_interactive.py` on Linux, macOS, and Windows:

  ```bash
  gh workflow run manual-tests.yml
  ```

* **Build and Release** ([`build-release.yml`](.github/workflows/build-release.yml)) — executes the test suite and then calls [`scripts/package_mac.sh`](scripts/package_mac.sh) and [`scripts/package_win.bat`](scripts/package_win.bat) to produce `Victoria.app.zip` and `Victoria.exe`. The workflow bundles everything in `dependencies/` except the README and publishes a GitHub release:

  ```bash
  gh workflow run build-release.yml
  ```

These packaging scripts can also be run locally if you need to build outside of GitHub.

## 🧠 Model Notes

| Model                     | Price (\$/1M tokens) | Category      | Best For              |
| ------------------------- | -------------------- | ------------- | --------------------- |
| **Google Gemini 2.5 Pro** | \$1.25 / \$10.00     | 🏆 Premium    | Best tested model     |
