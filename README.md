# Victoria x `crush` Setup

Victoria is Elcano's AI agent that connects to programmatic advertising reports via **MCP**. Paired with [`crush`](https://github.com/charmbracelet/crush), traders can ask powerful questions of CSVs, Excel files, and Snowflake datasets — making it easier to surface insights, spot trends, and optimize campaigns.

---

## ⚙️ Installation

### Linux / macOS

#### Dependencies

* `crush` – [GitHub](https://github.com/charmbracelet/crush)
* `uv` – [Docs](https://docs.astral.sh/uv/getting-started/installation/)
* `VICTORIA.md` – keep updated from the [victoria-main repo](https://github.com/ElcanoTek/victoria-main)
* `ghostty` – [ghostty.org](https://ghostty.org/) *(optional but recommended)*

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

## ▶️ Running Victoria

### Linux / macOS

```bash
cd victoria-crush
./victoria
```
---

### Windows

**Method 1: Double-Click (Easiest)**

1. Double-click `victoria.bat` in File Explorer
2. Follow the interactive prompts

**Method 2: PowerShell Direct**

```powershell
cd path\to\victoria-crush

# Main Victoria interface
.\victoria.ps1

# Install dependencies only
.\victoria.ps1 -InstallDeps

# Setup environment variables only
.\victoria.ps1 -Setup

# Skip dependency check
.\victoria.ps1 -SkipDependencyCheck
```

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
