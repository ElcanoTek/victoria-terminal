# Victoria x `crush` Setup

[![Test Victoria Script](https://github.com/ElcanoTek/victoria-crush/actions/workflows/test-victoria.yml/badge.svg)](https://github.com/ElcanoTek/victoria-crush/actions/workflows/test-victoria.yml)

Victoria is Elcano's AI agent that connects to programmatic advertising reports via **MCP**. Paired with [`crush`](https://github.com/charmbracelet/crush), traders can ask powerful questions of CSVs, Excel files, and Snowflake datasets — making it easier to surface insights, spot trends, and optimize campaigns.

---

## ⚙️ Installation

### Linux / macOS

#### Dependencies

* `ghostty` – [ghostty.org](https://ghostty.org/) *(optional but recommended)*
* `git` - open a terminal and type `git` to install it via Xcode on a Mac, if you are on Linux it should be preinstalled.
* `crush` – [GitHub](https://github.com/charmbracelet/crush)
* `uv` – [Docs](https://docs.astral.sh/uv/getting-started/installation/)
* `python` - open a terminal and type `python3` to install it via Xcode on a Mac, if you are on Linux it should be preinstalled. You may also download it from [python.org](https://www.python.org).

#### Environment Variables

* `OPENROUTER_API_KEY` (required)

  * Email [brad@elcanotek.com](mailto:brad@elcanotek.com) for a company key.
  * Example:

    ```bash
    # permanent (all sessions)
    # replace .zshrc with .bashrc if using bash
    echo 'export OPENROUTER_API_KEY="your_api_key_here"' >> ~/.zshrc
    source ~/.zshrc
    ```

* **Snowflake Integration (Optional)**

  ```bash
  export SNOWFLAKE_ACCOUNT="your_account_identifier"
  export SNOWFLAKE_USER="your_username@domain.com"
  export SNOWFLAKE_PASSWORD="your_password"
  export SNOWFLAKE_WAREHOUSE="your_warehouse"
  export SNOWFLAKE_ROLE="your_read_only_role"
  ```

  * **Role must have read-only `SELECT` permissions.**
  * Snowflake MCP server installs automatically on first use.

---

### Windows

#### Dependencies

* [Windows Terminal](https://aka.ms/terminal)
* [Git for Windows](https://git-scm.com/download/win)
* [crush](https://github.com/charmbracelet/crush)
* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* `python` - just open the windows terminal and type `python` to install or download the latest at [python.org](https://www.python.org/downloads/windows/)

#### Environment Variables

* `OPENROUTER_API_KEY` (required)

  ```powershell
  # Permanent (all sessions)
  [Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your_api_key_here", "User")
  ```

* **Snowflake Integration (Optional)**

  ```powershell
  [Environment]::SetEnvironmentVariable("SNOWFLAKE_ACCOUNT", "your_account", "User")
  [Environment]::SetEnvironmentVariable("SNOWFLAKE_USER", "your_user", "User")
  [Environment]::SetEnvironmentVariable("SNOWFLAKE_PASSWORD", "your_password", "User")
  [Environment]::SetEnvironmentVariable("SNOWFLAKE_WAREHOUSE", "your_warehouse", "User")
  [Environment]::SetEnvironmentVariable("SNOWFLAKE_ROLE", "your_role", "User")
  ```

  * **Role must have read-only `SELECT` permissions.**
  * Snowflake MCP server installs automatically on first use.

---

## 🚀 Launching Victoria

You can start Victoria in a couple of different ways, depending on your platform and comfort with the terminal.

### ▶️ From a Terminal (macOS, Linux, Windows)

Open your terminal, change into the `victoria-crush` folder, and run:

```bash
cd /path/to/victoria-crush
python3 victoria.py
```

This gives you the most control and is the same across macOS, Linux, and Windows (PowerShell).

#### Customizing the launch tool

Victoria uses the `crush` CLI by default. Set the following environment variables to swap in a different tool or config files:

```bash
export VICTORIA_TOOL="your_cli"
export VICTORIA_TEMPLATE="your_cli.template.json"
export VICTORIA_OUTPUT="your_cli.json"
```

---

### 🖱️ Double-Click (Windows)

For Windows users who prefer a one-click launch:

1. Open the `victoria-crush` folder.
2. Double-click `victoria.bat`.

That’s it — Victoria will start in a terminal window automatically.
*(If nothing happens, check that Python is installed and available in your PATH.)*

---

### 🖱️ Double-Click (macOS)

On macOS, you can launch Victoria from Finder:

1. Open the `victoria-crush` folder.
2. Double-click `victoria.command`.

> ⚠️ The first time, you may need to make the file executable:
>
> ```bash
> chmod +x victoria.command
> ```

After that, it’s double-click and go.

---

## 🧠 Models to Try

| Model                     | Price (\$/1M tokens) | Category      | Best For              |
| ------------------------- | -------------------- | ------------- | --------------------- |
| **gpt-oss-120b**          | \$0 / \$0.45         | 🆓 Free Input | Local experimentation |
| **GPT-5 Nano**            | \$0.05 / \$0.40      | ⚡ Ultra Fast  | Fast iteration        |
| **DeepSeek V3**           | \$0.27 / \$1.10      | 🎯 Best Value | Balanced performance  |
| **Google Gemini 2.5 Pro** | \$1.25 / \$10.00     | 🏆 Premium    | Best tested model     |

---

## ⚡ Quick Wins: Questions to Ask

Try these ready-to-go prompts for adtech analysis:

* **Performance Leaders**

  ```sql
  Provide the top 5 performing sites with over 5,000 impressions and the highest CTR, aggregated across the entire site rather than by individual day
  ```

* **Wasted Spend**

  ```sql
  Which placements had > 10,000 impressions but CTR below 0.05% and should be excluded from the buy?
  ```

* **Creative Insights**

  ```sql
  Compare CTR by creative size (300x250 vs 728x90 vs 160x600) across all campaigns last week
  ```

* **Publisher Quality**

  ```sql
  Show me the top 10 domains by spend that had a viewability score below 50%
  ```

* **Time-of-Day Analysis**

  ```sql
  Identify the best performing hours of the day (by CTR and CVR) across all campaigns
  ```

* **Conversion Optimization**

  ```sql
  Rank all campaigns by cost per conversion and highlight which campaigns are above the average CPA
  ```

* **Fraud & Anomalies**

  ```sql
  Flag any sites where impressions spiked 5x compared to the previous day but conversions did not increase
  ```

* **Budget Pacing**

  ```sql
  Estimate if each campaign is on pace to hit 100% of its budget by end of the month based on daily spend rates
  ```
